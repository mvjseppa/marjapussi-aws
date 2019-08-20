import simplejson as json
import boto3
import uuid
import os

from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
gameDb = dynamodb.Table(os.environ['DYNAMO_GAMES_TABLE'])


def _get_ws_details(event):
    req = event['requestContext']
    connection_id = req['connectionId'];
    endpoint_url = 'https://' + req['domainName'] + '/' + req['stage']
    return connection_id, endpoint_url


def _send_event_response(event, data):
    connection_id, endpoint_url = _get_ws_details(event)
    client = boto3.client('apigatewaymanagementapi', endpoint_url = endpoint_url)
    client.post_to_connection(
        ConnectionId=connection_id,
        Data=json.dumps(data).encode('utf-8')
    )


def connect(event, context):
    return { 'statusCode': 200 }


def disconnect(event, context):
    return { 'statusCode': 200 }


def handle_default(event, context):
    data = {'error': 'unknown action'}
    _send_event_response(event, data)

    return { 'statusCode': 200 }


def create_game(event, context):

    connectionId, _ = _get_ws_details(event)

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
    _send_event_response(event, {'id': item['id']})
    return { 'statusCode': 200 }


def get_game(event, context):
    body = json.loads(event['body'])
    id = body['id']

    try:
        response = gameDb.get_item(Key={'id': id})
        item = response['Item']
    except (KeyError, ClientError):
        item = None

    print(item)

    if item:
        _send_event_response(event, {'game': item})
    else:
        _send_event_response(event, {'error': 'not found'})

    return { 'statusCode': 200 }
