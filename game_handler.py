import simplejson as json
import boto3
import uuid
import os
import marjapussi

from event_utils import get_ws_details, send_event_response

from botocore.exceptions import ClientError

dynamo = boto3.resource('dynamodb')
game_db = dynamo.Table(os.environ['DYNAMO_GAMES_TABLE'])


def create_game(event, context):

    connection_id, _ = get_ws_details(event)

    game = marjapussi.MarjapussiGame()
    player_id = game.join(connection_id)

    db_item = game.to_dict_full()
    response_item = {
        "gameState": game.to_dict_for_player(player_id),
        "playerId": player_id
    }

    game_db.put_item(Item=db_item)
    send_event_response(event, response_item)
    return {'statusCode': 200}


def get_game(event, context):
    body = json.loads(event['body'])
    game_id = body['gameId']
    player_id = body['playerId']

    try:
        response = game_db.get_item(Key={'id': game_id})
        item = response['Item']
    except (KeyError, ClientError):
        item = None

    if item:
        response_item = marjapussi.MarjapussiGame.from_dict(item).to_dict_for_player(player_id)
        send_event_response(event, {'game': response_item})
    else:
        send_event_response(event, {'error': 'not found'})

    return {'statusCode': 200}
