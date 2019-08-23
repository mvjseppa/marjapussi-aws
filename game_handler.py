import simplejson as json
import boto3
import os
import marjapussi

from event_utils import get_ws_details, send_event_response, notify_clients_of_state_change

from botocore.exceptions import ClientError

dynamo = boto3.resource('dynamodb')
game_db = dynamo.Table(os.environ['DYNAMO_GAMES_TABLE'])


def create_game(event, context):

    connection_id, _ = get_ws_details(event)

    game = marjapussi.MarjapussiGame()
    player_id = game.join(connection_id)

    response_item = {
        "playerId": player_id,
        "gameState": game.to_dict_for_player(player_id)
    }

    game_db.put_item(Item=game.to_dict_full())
    send_event_response(event, response_item)
    return {'statusCode': 200}


def join_game(event, context):
    connection_id, _ = get_ws_details(event)
    body = json.loads(event['body'])
    try:
        player_id = body['playerId']
    except KeyError:
        player_id = None

    game = get_game_from_db(body['gameId'])

    if game is None:
        send_event_response(event, {'error': 'not found'})
        return {'statusCode': 200}

    if player_id:
        game.rejoin(player_id, connection_id)
    else:
        game.join(connection_id)

    if len([p for p in game.players if p is not None]) == 4:
        process_game_state_change(event, game, notify_only=True)
        game.deal()

    process_game_state_change(event, game)

    return {'statusCode': 200}


def play_card(event, context):
    body = json.loads(event['body'])
    game = get_game_from_db(body['gameId'])

    success = game.play_card(body['playerId'], body['card'])
    if not success:
        send_event_response(event, {'error': 'invalid play'})
        return {'statusCode': 200}

    else:
        process_game_state_change(event, game, notify_only=True)
        if game.trick_is_full():
            game.end_trick()
        process_game_state_change(event, game)

    return {'statusCode': 200}


def get_game_from_db(game_id):
    try:
        response = game_db.get_item(Key={'id': game_id})
        item = response['Item']
        return marjapussi.MarjapussiGame.from_dict(item)
    except (KeyError, ClientError):
        return None


def process_game_state_change(event, game, notify_only=False):
    if not notify_only:
        game_db.put_item(Item=game.to_dict_full())
    notify_clients_of_state_change(event, game)
