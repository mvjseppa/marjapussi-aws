from event_utils import send_event_response


def handle_default(event, context):
    data = {'type': 'ERROR', 'message': 'unknown action'}
    send_event_response(event, data)

    return {'statusCode': 200}
