#!/bin/bash

sudo apt-get update -y
sudo apt-get install -y python3-pip

cd /vagrant

pip3 install -r requirements.txt
