from boto3 import resource

# The boto3 dynamoDB resource
dynamodb_resource = resource('dynamodb')

def get_table(table_name: str):
    return dynamodb_resource.Table(table_name)

def add_item(table_name, col_dict):
    table = get_table(table_name)
    
    response = table.put_item(Item=col_dict)

    return response
