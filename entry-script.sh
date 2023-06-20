#!/bin/bash
sudo apt update -y
sudo apt upgrade -y
sudo apt install -y docker.io
sudo systemctl start docker
sudo usermod -aG docker ubuntu

sudo docker build -t your_docker_username/python-server .
sudo docker push your_docker_username/python-server