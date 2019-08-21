import simplejson as json
import boto3
import uuid
import os

from event_utils import get_ws_details, send_event_response

from botocore.exceptions import ClientError

dynamo = boto3.resource('dynamodb')
game_db = dynamo.Table(os.environ['DYNAMO_GAMES_TABLE'])


def create_game(event, context):

    connection_id, _ = get_ws_details(event)

    item = {
        'id': str(uuid.uuid1()),
        'gameState': new_game
    }

    game_db.put_item(Item=item)
    send_event_response(event, {'id': item['id']})
    return { 'statusCode': 200 }


def get_game(event, context):
    body = json.loads(event['body'])
    game_id = body['id']

    try:
        response = game_db.get_item(Key={'id': game_id})
        item = response['Item']
    except (KeyError, ClientError):
        item = None

    print(item)

    if item:
        send_event_response(event, {'game': item})
    else:
        send_event_response(event, {'error': 'not found'})

    return { 'statusCode': 200 }
