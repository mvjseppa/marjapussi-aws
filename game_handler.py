import simplejson as json
import boto3
import uuid
import os

from event_utils import get_ws_details, send_event_response

from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
gameDb = dynamodb.Table(os.environ['DYNAMO_GAMES_TABLE'])


def create_game(event, context):

    connectionId, _ = get_ws_details(event)

    newGame = {
      'players': {'1': connectionId, '2': None, '3': None, '4': None},
      'hands': {'1': ['ab', 'cd'], '2': ['ef', 'gh'], '3': ['ij'], '4': ['J']},
      'table': [],
      'discard': [],
      'turn': 0
    }

    item = {
        'id': str(uuid.uuid1()),
        'gameState': newGame
    }

    gameDb.put_item(Item=item)
    send_event_response(event, {'id': item['id']})
    return { 'statusCode': 200 }


def get_game(event, context):
    body = json.loads(event['body'])
    game_id = body['id']

    try:
        response = gameDb.get_item(Key={'id': game_id})
        item = response['Item']
    except (KeyError, ClientError):
        item = None

    print(item)

    if item:
        send_event_response(event, {'game': item})
    else:
        send_event_response(event, {'error': 'not found'})

    return { 'statusCode': 200 }
