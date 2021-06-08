import joblib
import os
from boto3 import resource
import time
from dynamodb import query_table, add_first_item
from url_handler import UrlHandler

DDB_TABLE = os.environ['DYNAMODB_TABLE_NAME']
BUCKET_NAME = os.environ['BUCKET_NAME']
BUCKET_KEY = os.environ['BUCKET_KEY']

PICKLE_PATH = '/tmp/model.pkl'

def load_pickle_to_s3() -> None:
    s3 = resource('s3')
    s3.Bucket(BUCKET_NAME).download_file(BUCKET_KEY, PICKLE_PATH)

def load_model():
    load_pickle_to_s3()
    return joblib.load(PICKLE_PATH)

def lambdaHandler(event, context) -> dict:

    links = event['source_links']

    model = load_model()

    for link in links:

        try:
            data = query_table(DDB_TABLE, filter_key='link', filter_value=link) 
            print(data)   
            prediction = model.predict([data])
            prediction = prediction.tolist()
            response = str(prediction[0])

        except:
            add_first_item(DDB_TABLE, link)
            response = UrlHandler(link).generate_data()

    return {'body': response, 'statusCode': 200}