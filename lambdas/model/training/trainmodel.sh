docker build . -f Dockerfile -t model
IMAGE_ID=$(docker images -q model)
docker run -d --name 'training' ${IMAGE_ID} 'training.lambdaHandler'
docker cp .:/var/task/model.pkl model.pkl
docker kill training && docker rm training