import boto3
import simplejson as json
import marjapussi


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


def notify_clients_of_state_change(event, game_state: marjapussi.MarjapussiGame):
    _, endpoint_url = get_ws_details(event)
    client = boto3.client('apigatewaymanagementapi', endpoint_url=endpoint_url)

    for player in game_state.players:
        if player is None:
            continue
        data = json.dumps(
            {
                "playerId": player.id,
                "gameState": game_state.to_dict_for_player(player.id)
            }
        ).encode('utf-8')
        connection_id = player.connection_id

        client.post_to_connection(
            ConnectionId=connection_id,
            Data=data
        )

