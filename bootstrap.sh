#!/bin/bash
set -e

ufw disable

apt-get update -y
apt-get install -y build-essential libssl-dev python3-pip python3.10-venv ca-certificates ntpdate cron

ntpdate time.google.com
update-ca-certificates

cd /vagrant
python3 -m venv venv
/vagrant/venv/bin/pip install --upgrade pip setuptools wheel
/vagrant/venv/bin/pip install -r /vagrant/requirements.txt

cp /vagrant/dns-shortener.service /etc/systemd/system/dns-shortener.service
systemctl daemon-reload
systemctl enable dns-shortener.service
systemctl start dns-shortener.service

CRON_JOB="* * * * * vagrant /vagrant/venv/bin/python3 /vagrant/sync_dns.py >> /vagrant/cron.log 2>&1"
echo "$CRON_JOB" > /etc/cron.d/dns-sync
chmod 0644 /etc/cron.d/dns-sync

touch /vagrant/cron.log
chown vagrant:vagrant /vagrant/cron.log
chmod 666 /vagrant/cron.log

systemctl enable cron
systemctl restart cron

if ! ping -c 4 google.com > /dev/null 2>&1; then
  exit 1
fi