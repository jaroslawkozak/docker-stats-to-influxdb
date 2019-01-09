#!/usr/bin/python
import os
os.system('sudo docker stop docker-stats')
os.system('sudo docker rm docker-stats')
os.system('sudo docker image rm docker-stats')
os.system('sudo docker build --no-cache . -f Dockerfile-rpi -t docker-stats:latest')
os.system('sudo docker run --privileged --name docker-stats -d docker-stats')


