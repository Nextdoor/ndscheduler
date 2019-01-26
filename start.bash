DEBUG=0
if [ "$1" = "-d" ];then
    DEBUG=1
fi
./build.sh
DEBUG=$DEBUG docker-compose up