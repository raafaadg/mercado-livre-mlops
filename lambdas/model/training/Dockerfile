FROM public.ecr.aws/lambda/python:3.8
COPY training.py requirements.txt utils/. ./
RUN pip3 install -r requirements.txt
CMD ["training.lambdaHandler"]