#!/bin/bash

apt-get update -y

apt-get install -y python3-pip python3.10-venv

cd /vagrant

python3 -m venv venv

source venv/bin/activate
pip install -r requirements.txt

