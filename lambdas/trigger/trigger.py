#! /usr/bin/python3.8 Python3.8
import json
from utils.url_handler import UrlHandler
import logging
from typing import Any, Dict, List, Optional

from utils.dynamodb import add_item

logger = logging.getLogger()
logger.setLevel(logging.WARNING)

def lambda_handler(event: dict, context: Any):
    response: Dict[str, Any] = {}

    try:
        print('REQUEST EVENT:')
        print(json.dumps(event))

        parsers = {
            'INSERT': parse_new_item
            ,'MODIFY': parse_modified_item
            ,'REMOVE': None
        }

        response['return'] = 'Fail'

        for record in event.get('Records', []):

            if record['eventSource'] == 'aws:dynamodb':

                parser = parsers.get(record.get('eventName'))
                if parser != None:
                    parser(record=record)

                    response['return'] = 'Success'

    except Exception as error:
        logger.exception(error)

        response['return'] = error

    finally:
        print('RESPONSE:')
        print(json.dumps(response))

        return response

def calculate_formulas(link: str, appearances: int) -> dict:
    return UrlHandler(link,appearances).generate_data()


def parse_new_item(record) -> None:
    item = record['dynamodb']['NewImage']
    link = item.get('link', {}).get('S')
    appearances = item.get('appearances', {}).get('N')

    data = calculate_formulas(link, appearances)
    add_item('mercado-libre-link-table', data)

def parse_modified_item(record) -> None:
    item = record['dynamodb']['NewImage']
    if len(item) == 2:
        parse_new_item(record)
