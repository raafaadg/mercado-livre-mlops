import requests
import re
import json
from utils.dynamodb import add_appearances 
import os
import boto3

client = boto3.client('sns')

try:
    ddb_table = os.environ['DYNAMODB_TABLE_NAME']
    topic_arn = os.environ['TOPIC_ARN']
except:
    ddb_table = ''
    topic_arn = ''

def publish(link: str, level: int) -> None:
    links = get_refs_from_link(link)
    [publish_topic({
        "link":link, "level":level
    }) for link in links]


def publish_topic(message: str):
    print(f'Publishing {message}')
    response = client.publish(
        TargetArn=topic_arn,
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json'
    )
    return response

def get_refs_from_link(link) -> list:

    ret = requests.get(link).text.replace('>', '>\n')

    link_pattern = re.compile('href="([http].*)"',re.ASCII)
    slash_pattern = re.compile('href="([/].*)"',re.ASCII)

    links_normal = link_pattern.findall(ret)
    slash_link = [link+sl[1:] for sl in slash_pattern.findall(ret)]

    return links_normal + slash_link


def main(event) -> str:
    try:
        for record in event['Records']:
            link = json.loads(json.loads(record['body'])['Message'])['link']
            level = int(json.loads(json.loads(record['body'])['Message'])['level'])
            print(link,level)
            add_appearances(ddb_table, link)
            if level > 0:
                publish(link, level-1)         
        return {'body': 'Success', 'statusCode': 200}
    except:
        return {'body': 'Erro', 'statusCode': 200}

def lambda_handler(event, context):
    return main(event)
