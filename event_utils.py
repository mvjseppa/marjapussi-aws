import boto3
import simplejson as json


def get_ws_details(event):
    req = event['requestContext']
    connection_id = req['connectionId'];
    endpoint_url = 'https://' + req['domainName'] + '/' + req['stage']
    return connection_id, endpoint_url


def send_event_response(event, data):
    connection_id, endpoint_url = get_ws_details(event)
    client = boto3.client('apigatewaymanagementapi', endpoint_url=endpoint_url)
    client.post_to_connection(
        ConnectionId=connection_id,
        Data=json.dumps(data).encode('utf-8')
    )
