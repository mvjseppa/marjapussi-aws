import simplejson as json
import boto3
import os
import marjapussi

from event_utils import get_ws_details, send_event_response, notify_clients_of_state_change

from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr

dynamo = boto3.resource('dynamodb')
game_db = dynamo.Table(os.environ['DYNAMO_GAMES_TABLE'])


def create_game(event, context):

    connection_id, _ = get_ws_details(event)

    body = json.loads(event['body'])
    try:
        player_name = body['playerName']
    except KeyError:
        send_event_response(event, {'type': 'error', 'message': 'Missing player name.'})
        return {'statusCode': 200}

    game = marjapussi.MarjapussiGame()
    player_id = game.join(player_name, connection_id)

    response_item = {
        "type": "UPDATE_GAME_STATE",
        "playerId": player_id,
        "gameState": game.to_dict_for_player(player_id)
    }

    put_state_to_db(game)
    send_event_response(event, response_item)
    return {'statusCode': 200}


def join_game(event, context):
    connection_id, _ = get_ws_details(event)
    body = json.loads(event['body'])
    try:
        player_id = body['playerId']
    except KeyError:
        player_id = None

    try:
        player_name = body['playerName']
    except KeyError:
        send_event_response(event, {'type': 'error', 'message': 'Missing player name.'})
        return {'statusCode': 200}

    game = get_game_from_db(body['gameId'])

    if game is None:
        send_event_response(event, {'type': 'ERROR', 'message': 'not found'})
        return {'statusCode': 200}

    if player_id:
        game.rejoin(player_id, connection_id)
    else:
        game.join(player_name, connection_id)

    notify_clients_of_state_change(event, game)

    if len([p for p in game.players if p is not None]) == 4:
        game.deal()
        notify_clients_of_state_change(event, game)

    put_state_to_db(game)

    return {'statusCode': 200}


def play_card(event, context):
    body = json.loads(event['body'])
    game = get_game_from_db(body['gameId'])

    success = game.play_card(body['playerId'], body['card'])
    if not success:
        send_event_response(event, {'type': 'ERROR', 'message': 'invalid play'})
        return {'statusCode': 200}

    else:
        notify_clients_of_state_change(event, game)
        if game.trick_is_full():
            game.end_trick()
            notify_clients_of_state_change(event, game)

        put_state_to_db(game)

    return {'statusCode': 200}


def list_games(event, context):
    scan_result = game_db .scan(FilterExpression=Attr('players').contains(None))

    response = {
        'type': 'GAME_LIST_READY',
        'gameList': [
            {
                'id': i['id'],
                'name': i['name']
            } for i in scan_result['Items']
        ]
    }
    send_event_response(event, response)

    return {'statusCode': 200}


def get_game_from_db(game_id):
    try:
        response = game_db.get_item(Key={'id': game_id})
        item = response['Item']
        return marjapussi.MarjapussiGame.from_dict(item)
    except (KeyError, ClientError):
        return None


def put_state_to_db(game):
    game_db.put_item(Item=game.to_dict_full())
