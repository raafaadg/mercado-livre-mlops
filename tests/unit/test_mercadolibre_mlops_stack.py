import json
import pytest

from aws_cdk import core
from mercado_libre_mlops.mercado_libre_mlops_stack import MercadoLibreMlopsStack

STACK_NAME = 'mercado-libre-mlops'

def get_template():
    app = core.App()
    MercadoLibreMlopsStack(app, STACK_NAME)
    return json.dumps(app.synth().get_stack(STACK_NAME).template)


def test_sqs_queue_created():
    assert("AWS::SQS::Queue" in get_template())


# def test_sns_topic_created():
#     assert("AWS::SNS::Topic" in get_template())
