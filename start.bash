DEBUG=0
if [ "$1" = "-d" ];then
    DEBUG=1
fi
./build.sh
if [ ! "$(docker network ls | grep in2it)" ]; then
  docker network create in2it
fi
DEBUG=$DEBUG docker-compose up