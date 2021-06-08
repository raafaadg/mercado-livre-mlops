FROM public.ecr.aws/lambda/python:3.8
COPY app.py requirements.txt utils/. ./
RUN pip3 install -r requirements.txt
CMD ["app.lambdaHandler"]