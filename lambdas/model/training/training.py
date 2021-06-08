import ast
import os
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
from boto3 import resource
from boto3.dynamodb.conditions import Key
from dynamodb import full_scan

BUCKET_NAME = os.environ['BUCKET_NAME']
BUCKET_KEY = os.environ['BUCKET_KEY']
ddb_table = os.environ['DYNAMODB_TABLE_NAME']

dynamodb_resource = resource('dynamodb')
s3 = resource('s3')

def save_pickle_to_s3(model): 
    joblib.dump(model, '/tmp/model.pkl')
    s3.meta.client.upload_file('/tmp/model.pkl', BUCKET_NAME, BUCKET_KEY)

def load_data():
    df = full_scan(ddb_table)
    return df

def lambdaHandler(event, context) -> dict:
    print(event)

    df = load_data()
    df = df.drop('link', axis=1).dropna().drop_duplicates(keep="first")

    train_set, test_set = train_test_split(df, test_size=0.3, random_state=42)

    train_set_no_labels = train_set.drop("appearances", axis=1)
    train_set_labels = train_set["appearances"].copy()

    model = RandomForestClassifier(n_estimators=100, max_depth=10, n_jobs=-1, criterion='entropy')
    model.fit(train_set_no_labels, train_set_labels)

    save_pickle_to_s3(model)

    return {'body': 'New Model Version Trained!', 'statusCode': 200}
