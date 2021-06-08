import ast
from boto3 import resource
import json
import decimal

dynamodb_resource = resource('dynamodb')

def get_table(table_name: str):
    return dynamodb_resource.Table(table_name)

def get_table_metadata(table_name):
    table = get_table(table_name)

    return {
        'num_items': table.item_count,
        'primary_key_name': table.key_schema[0],
        'status': table.table_status,
        'bytes_size': table.table_size_bytes,
        'global_secondary_indices': table.global_secondary_indexes
    }


def read_table_item(table_name, pk_name, pk_value):
    table = get_table(table_name)
    response = table.get_item(Key={pk_name: pk_value})

    return response

def add_first_item(table_name, link):
    col_dict = {
        "link":link,
        "appearances":1,
    }
    response = add_item(table_name, col_dict)
    return response

def add_item(table_name, col_dict):
    table = get_table(table_name)
    
    response = table.put_item(Item=col_dict)

    return response


def delete_item(table_name, pk_name, pk_value):
    table = get_table(table_name)
    response = table.delete_item(Key={pk_name: pk_value})

    return response

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def literal(i):
    return ast.literal_eval((json.dumps(i, cls=DecimalEncoder)))        
     
def parser(item):
    aux={}
    for it in item.items():
        aux[it[0]] = literal(it[1])
    return aux

def get_table(table_name: str):
    return dynamodb_resource.Table(table_name)

def add_appearances(table_name, link):
    print("add_appearances")
    table = get_table(table_name)
    response = table.update_item(
        Key={'link': link},
        UpdateExpression='ADD appearances :appearances',
        ExpressionAttributeValues={':appearances': 1}
    )
    return response