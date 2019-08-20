import simplejson as json
import boto3
import uuid
import os

from botocore.exceptions import ClientError
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
gameDb = dynamodb.Table(os.environ['DYNAMO_GAMES_TABLE'])

def _getWsDetails(event):
    req = event['requestContext']
    connectionId = req['connectionId'];
    endpointUrl = 'https://' + req['domainName'] + '/' + req['stage']
    return connectionId, endpointUrl

def _sendEventResponse(event, data):
    connectionId, endpointUrl = _getWsDetails(event)
    client = boto3.client('apigatewaymanagementapi', endpoint_url = endpointUrl)
    client.post_to_connection(
        ConnectionId = connectionId,
        Data = json.dumps(data).encode('utf-8')
    )

def connect(event, context):
    return { 'statusCode': 200 }

def disconnect(event, context):
    return { 'statusCode': 200 }

def handleDefault(event, context):
    data = {'error': 'unknown action'}
    _sendEventResponse(event, data)

    return { 'statusCode': 200 }

def createGame(event, context):

    connectionId, _ = _getWsDetails(event)

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
    _sendEventResponse(event, {'id': item['id']})
    return { 'statusCode': 200 }



def getGame(event, context):
    body = json.loads(event['body'])
    id = body['id']

    try:
        response = gameDb.get_item(Key={'id': id})
        item = response['Item']
    except (KeyError, ClientError):
        item = None

    print(item)

    if(item):
        _sendEventResponse(event, {'game': item})
    else:
        _sendEventResponse(event, {'error': 'not found'})

    return { 'statusCode': 200 }
