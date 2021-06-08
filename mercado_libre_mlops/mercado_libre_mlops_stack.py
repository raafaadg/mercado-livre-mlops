from re import T
from aws_cdk.aws_lambda_python import PythonFunction
from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as _api_gw,
    aws_apigatewayv2 as api_gw,
    aws_apigatewayv2_integrations as integrations,
    aws_dynamodb,
    aws_sqs,
    aws_sns,
    aws_sns_subscriptions,
    aws_lambda_event_sources,
    aws_logs,
    aws_s3,
    core
)
import os


class MercadoLibreMlopsStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.ddb_attr_time_to_live = 'time-to-live'

        self.ddb_param_max_parallel_streams = 5

        self.ddb_retry_attempts = 2

        self.ddb_batch_size = 50

        self.method_response = {
            'statusCode': '200',
            'responseParameters': {
                'method.response.header.Access-Control-Allow-Origin': True
            }
        }

        self.integration_response = {
            'statusCode': '200',
            'responseParameters': {
            'method.response.header.Access-Control-Allow-Origin': "'*'"
            }
        }

        self.create_cdk_resources()

    def create_bucket(self):
        self.model_bucket = aws_s3.Bucket(
            self,
            'MercadoLibreModelBucket',
            bucket_name = 'mercadolibre-mlops-test-model-store'
        )

    def create_lambdas(self) -> None:
        self.model_folder = os.path.dirname(os.path.realpath(__file__)) + "/../lambdas/model/predict"
        self.predictive_lambda = _lambda.DockerImageFunction(self,
                                                        'PredictiveLambda',
                                                        code=_lambda.DockerImageCode.from_image_asset(self.model_folder),
                                                        memory_size=1024,
                                                        timeout=core.Duration.seconds(60),
                                                        environment={
                                                            'DYNAMODB_TABLE_NAME': self.ddb_table.table_name,
                                                            'TOPIC_ARN': self.sns.topic_arn,
                                                            'TOPIC_NAME': self.sns.topic_name,
                                                            'BUCKET_NAME': self.model_bucket.bucket_name,
                                                            "BUCKET_KEY": 'model/model.pkl'
                                                        })

        self.train_folder = os.path.dirname(os.path.realpath(__file__)) + "/../lambdas/model/training"
        self.train_lambda = _lambda.DockerImageFunction(self,
                                                        'TrainLambda',
                                                        code=_lambda.DockerImageCode.from_image_asset(self.train_folder),
                                                        memory_size=4096,
                                                        timeout=core.Duration.minutes(10),
                                                        environment={
                                                            'DYNAMODB_TABLE_NAME': self.ddb_table.table_name,
                                                            'TOPIC_ARN': self.sns.topic_arn,
                                                            'TOPIC_NAME': self.sns.topic_name,
                                                            'BUCKET_NAME': self.model_bucket.bucket_name,
                                                            "BUCKET_KEY": 'model/model.pkl'
                                                        })

        self.base_lambda = PythonFunction(self,'ApiLambda',
            handler='lambda_handler',
            index="main.py",
            runtime=_lambda.Runtime.PYTHON_3_8,
            entry = './lambdas/api',
            environment={
                'DYNAMODB_TABLE_NAME': self.ddb_table.table_name,
                'TOPIC_ARN': self.sns.topic_arn,
                'TOPIC_NAME': self.sns.topic_name
            }
        )

        self.scrap_lambda = PythonFunction(
            self,
            'ScrapLambda',
            handler='lambda_handler',
            index="main.py",
            runtime=_lambda.Runtime.PYTHON_3_8,
            entry = './lambdas/scraper',
            environment={
                'DYNAMODB_TABLE_NAME': self.ddb_table.table_name,
                'TOPIC_ARN': self.sns.topic_arn,
                'TOPIC_NAME': self.sns.topic_name
            }
        )

        self.scrap_lambda.add_event_source(
            aws_lambda_event_sources.SqsEventSource(
                self.sqs
            )
        )

        self.trigger_lambda = _lambda.Function(self,'TriggerLambda',
            handler='trigger.lambda_handler',
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset('lambdas/trigger'),
            log_retention=aws_logs.RetentionDays.ONE_WEEK,
            reserved_concurrent_executions=self.ddb_param_max_parallel_streams,
            events=[self.ddb_event_lamb],
            environment={}
        )

    def create_rest_api(self) -> None:

        self.base_api = _api_gw.RestApi(
            self
            ,'PredictiveLambdaEndpoint'
            ,rest_api_name='PredictiveLambdaEndpoint'
            ,endpoint_types  = [_api_gw.EndpointType.REGIONAL]
        )

        self.model_base = self.base_api.root.add_resource('predict')
        self.api_base = self.base_api.root.add_resource('api')
        self.traind_base = self.base_api.root.add_resource('train')

        self.model_lambda_integration = _api_gw.LambdaIntegration(
            self.predictive_lambda,
            proxy=False,
            integration_responses=[self.integration_response]
        )

        self.train_lambda_integration = _api_gw.LambdaIntegration(
            self.train_lambda,
            proxy=False,
            integration_responses=[self.integration_response]
        )

        self.model_base.add_method(
            'GET',
            self.model_lambda_integration, 
            method_responses=[self.method_response]
        )

        self.traind_base.add_method(
            'POST',
            self.train_lambda_integration, 
            method_responses=[self.method_response]
        )

        self.api_lambda_integration = _api_gw.LambdaIntegration(
            self.base_lambda,
            proxy=True
        )

        self.api_base.add_method(
            'ANY',
            self.api_lambda_integration
        )
        

    def create_dynamodb(self) -> None:
        
        self.ddb_table = aws_dynamodb.Table(
            self,
            'mercadolivre-dynamo-table',
            table_name ='mercado-libre-link-table',
            partition_key=aws_dynamodb.Attribute(
                name='link',
                type=aws_dynamodb.AttributeType.STRING,
            ),
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery=True,
            removal_policy=core.RemovalPolicy.DESTROY,
            time_to_live_attribute=self.ddb_attr_time_to_live,
            stream=aws_dynamodb.StreamViewType.NEW_IMAGE
        )

    def grant_dynamodb_permissions(self) -> None:

        self.ddb_table.grant_read_write_data(self.base_lambda)
        self.ddb_table.grant_read_write_data(self.trigger_lambda)
        self.ddb_table.grant_read_write_data(self.scrap_lambda)
        self.ddb_table.grant_read_write_data(self.predictive_lambda)
        self.ddb_table.grant_read_write_data(self.train_lambda)

    def grant_msg_permissions(self) -> None:

        self.sqs.grant_send_messages(self.base_lambda)
        self.sqs.grant_send_messages(self.scrap_lambda)
        self.sqs.grant_consume_messages(self.base_lambda)
        self.sqs.grant_consume_messages(self.scrap_lambda)

        self.sns.grant_publish(self.scrap_lambda)
        self.sns.grant_publish(self.base_lambda)

    def create_messaging(self) -> None:
        self.sqs = aws_sqs.Queue(
            self,
            'Mercadolivre-SQS',
            retention_period=core.Duration.days(14),
            visibility_timeout=core.Duration.minutes(15)
        )

        self.sns = aws_sns.Topic(
            self,
            'Mercadolivre-SNS'
        )

        self.sns.add_subscription(aws_sns_subscriptions.SqsSubscription(self.sqs))

    def add_events(self) -> None:
        self.ddb_event_lamb = aws_lambda_event_sources.DynamoEventSource(
            table=self.ddb_table,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=self.ddb_batch_size,
            max_batching_window=core.Duration.seconds(60),
            parallelization_factor=self.ddb_param_max_parallel_streams,
            retry_attempts=self.ddb_retry_attempts
        )

    def grant_bucket_permissions(self) -> None:

        self.model_bucket.grant_put(self.predictive_lambda)   
        self.model_bucket.grant_put(self.train_lambda)   

        self.model_bucket.grant_read(self.predictive_lambda)   
        self.model_bucket.grant_read(self.train_lambda)   

    def create_cdk_resources(self) -> None:
        self.create_bucket()
        self.create_dynamodb()
        self.create_messaging()
        self.add_events()
        self.create_lambdas()
        self.create_rest_api()
        self.grant_dynamodb_permissions()
        self.grant_msg_permissions()    
        self.grant_bucket_permissions()    

