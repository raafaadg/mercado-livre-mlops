import boto3
from time import gmtime, strftime

sagemaker = boto3.client('sagemaker')
endpoint_config_name = 'MeliMlopsEndpointConfig-' + strftime("%Y-%m-%d-%H-%M-%S", gmtime())
model_name = 'MeLiMLopsModel'
print(endpoint_config_name)
create_endpoint_config_response=sagemaker.create_endpoint_config(
    EndpointConfigName=endpoint_config_name,
    ProductionVariants=[{
        'InstanceType':'ml.m4.xlarge',
        'InitialInstanceCount':1,
        'ModelName':model_name,
        'VariantName':'AllTraffic',
        'AcceleratorType':'ml.eia1.medium'}])

print("Endpoint Config Arn: " + create_endpoint_config_response['EndpointConfigArn'])

endpoint_name = 'MeliMlopsEndpoint-' + strftime("%Y-%m-%d-%H-%M-%S", gmtime())
endpoint_response = sagemaker.create_endpoint(
    EndpointName=endpoint_name,
    EndpointConfigName=endpoint_config_name)