import boto3
import json
from datetime import date, datetime, timedelta
from urllib.request import Request, urlopen
import os
from http.client import HTTPResponse


def run(event, context):
    message = {'text': json.dumps(event['detail'], default=_json_serial, indent=4)}
    url = _get_webhook_url()
    response = _send_message(json.dumps(message, default=_json_serial), url)
    print('[run]response {}'.format(json.dumps(response, default=_json_serial)))
    return json.loads(json.dumps(response, default=_json_serial))


def _send_message(message, webhookurl):
    request = Request(
        webhookurl,
        data=message.encode('UTF-8'),
        method="POST"
    )
    with urlopen(request) as response:
        response_body = response.read().decode('utf-8')
    print('[send_message]response {}'.format(json.dumps(response_body, default=_json_serial)))
    return response


def _get_webhook_url():
    param_name = os.environ.get('WEBHOOKURL_PARAM_NAME')
    client = boto3.client('ssm')
    response = client.get_parameter(
        Name=param_name,
        WithDecryption=True
    )
    param = response.get('Parameter')
    if param:
        return param.get('Value')
    else:
        return None


def _json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, HTTPResponse):
        return obj.read().decode('utf-8')
    raise TypeError ("Type %s not serializable" % type(obj))
