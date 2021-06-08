from flask import Flask, request, Response
import boto3
import json
import logging
import aws_lambda_wsgi
import os

client = boto3.client('sns')

ddb_table = os.environ['DYNAMODB_TABLE_NAME']
topic_arn = os.environ['TOPIC_ARN']

logger = logging.getLogger()
logger.setLevel('INFO')

meli_app = Flask('meli_app')


def publish_topic(message: str):
    response = client.publish(
        TargetArn=topic_arn,
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json'
    )
    return response

def api_response(resp_dict, status_code):
    response = Response(json.dumps(resp_dict), status_code)
    response.headers["Content-Type"] = "application/json"
    return response


@meli_app.route('/api/', methods=["POST"])
def check_status():

    links = request.json.get('source_links')
    level = request.json.get('level')

    for link in links:
        publish_topic({"link":link, "level":level})

    return api_response('Job Started', 200)

def lambda_handler(event, context):
    return aws_lambda_wsgi.response(meli_app, event, context)

if __name__ == "__main__":
    meli_app.run(debug=True, port=8080)
