import boto3
import simplejson as json
import marjapussi
from botocore.exceptions import ClientError


def get_ws_details(event):
    req = event['requestContext']
    connection_id = req['connectionId']
    endpoint_url = 'https://' + req['domainName'] + '/' + req['stage']
    return connection_id, endpoint_url


def send_event_response(event, data):
    connection_id, endpoint_url = get_ws_details(event)
    client = boto3.client('apigatewaymanagementapi', endpoint_url=endpoint_url)
    client.post_to_connection(
        ConnectionId=connection_id,
        Data=json.dumps(data).encode('utf-8')
    )


def notify_clients_of_state_change(event, game_state: marjapussi.MarjapussiGame):
    _, endpoint_url = get_ws_details(event)
    client = boto3.client('apigatewaymanagementapi', endpoint_url=endpoint_url)

    for player in game_state.players:
        if player is None:
            continue
        data = json.dumps(
            {
                'type': 'UPDATE_GAME_STATE',
                'playerId': player.id,
                'gameId': game_state.id,
                'gameState': game_state.to_dict_for_player(player.id)
            }
        ).encode('utf-8')

        try:
            client.post_to_connection(
                ConnectionId=player.connection_id,
                Data=data
            )
        except ClientError:
            continue
