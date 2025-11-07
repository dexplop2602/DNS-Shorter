#!/bin/bash

apt-get update -y
apt-get install -y python3-pip python3.10-venv

cd /vagrant

python3 -m venv venv
/vagrant/venv/bin/pip install -r /vagrant/requirements.txt > /dev/null 2>&1

cp /vagrant/dns-shortener.service /etc/systemd/system/dns-shortener.service

systemctl daemon-reload

systemctl enable dns-shortener.service

systemctl start dns-shortener.service