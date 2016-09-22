#!/bin/bash

# This script installs the tech stack for the CytoscapeNAV web application, starting from a new Amazon Linux AMI.

# Assumptions
# 1. you have mounted a volume under /home/ec2-user/data
# 2. you have cloned the repository as /home/ec2-user/data/cytoscapenav

sudo yum update -y

cd ~/data/cytoscapenav

# initialize and update submodules
git submodule init
git submodule update

cd ~/data

# install python
wget https://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh
chmod +x Miniconda-latest-Linux-x86_64.sh
./Miniconda-latest-Linux-x86_64.sh -b -p ~/data/miniconda

# need to install python on the path for root
sudo rm /usr/bin/python
sudo ln -s /home/ec2-user/data/miniconda/bin/python /usr/bin/python

echo "export PATH=\"/home/ubuntu/data/miniconda/bin:\$PATH\"" >> ~/.bashrc
source ~/.bashrc
#conda install pip -y # already installed by default
conda install numpy -y
conda install scipy -y
#conda install pymongo -y # still on version 2.8
pip install pymongo # version 3.0
#conda install requests -y # already installed by default
conda install gevent -y
conda install gevent-websocket -y
pip install bottle

echo "install mongodb"
echo "[mongodb-org-3.0]" > mongodb-org-3.0.repo
echo "name=MongoDB Repository" >> mongodb-org-3.0.repo
echo "baseurl=https://repo.mongodb.org/yum/amazon/2013.03/mongodb-org/3.0/x86_64/" >> mongodb-org-3.0.repo
echo "gpgcheck=0" >> mongodb-org-3.0.repo
echo "enabled=1" >> mongodb-org-3.0.repo
sudo mv mongodb-org-3.0.repo /etc/yum.repos.d
sudo chown root /etc/yum.repos.d/mongodb-org-3.0.repo
sudo chgrp root /etc/yum.repos.d/mongodb-org-3.0.repo
sudo yum install mongodb-org -y
mkdir /home/ec2-user/data/mongo # database location

cd ~/data/cytoscapenav/bin
./start-mongodb.sh
./load-genemania.sh
./load-humannet.sh
./load-go.sh
sudo ./start-server.sh # sudo required for port 80