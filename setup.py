import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="mercado_libre_mlops",
    version="0.0.1",

    description="Mercado Libre Mlops Test",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Rafael Goncalves",

    package_dir={"": "mercado_libre_mlops"},
    packages=setuptools.find_packages(where="mercado_libre_mlops"),

    install_requires=[
        "aws-cdk.core",
        "aws-cdk.aws_apigateway",
        "aws-cdk.aws_apigatewayv2",
        "aws-cdk.aws-apigatewayv2-integrations",
        "aws-cdk.aws-lambda",
        "aws-cdk.aws-dynamodb",
        "aws-cdk.aws-sqs",
        "aws-cdk.aws-sns",
        "aws-cdk.aws-sns-subscriptions",
        "aws-cdk.aws-lambda-event-sources",
        "aws-cdk.aws-lambda-destinations",
        "aws-cdk.aws-lambda-python",
        "aws-cdk.aws-logs",
        "aws-cdk.aws-s3",
        "aws-cdk.aws-secretsmanager",
        "aws-cdk.aws-codepipeline-actions",
        "aws-cdk.aws-ssm",
        "scikit-learn",
        "flask",
        "aws_lambda_wsgi",
        "flask-restful",
        "SQLAlchemy",
        "aws_lambda_wsgi",
        "boto3",
        "path"
    ],

    python_requires=">=3.7",

    classifiers=[
        "Development Status :: 1 - Beta",

        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

    ],
)
