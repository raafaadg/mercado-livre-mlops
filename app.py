#!/usr/bin/env python

from aws_cdk import core

from mercado_libre_mlops.mercado_libre_mlops_stack import MercadoLibreMlopsStack
from mercado_libre_mlops.mercado_libre_mlops_pipeline import MercadoLibreMlopsPipeline

env_USA = core.Environment(account='166202287709', region="us-east-1")

app = core.App()
MercadoLibreMlopsStack(app, "mercado-libre-mlops")
MercadoLibreMlopsPipeline(app, "mercado-libre-mlops-pipeline", env=env_USA)

app.synth()
