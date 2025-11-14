#!/bin/bash
set -e

# ... (toda la instalación de paquetes, certificados, hora, etc. se mantiene igual) ...
apt-get update -y
apt-get install -y build-essential libssl-dev python3-pip python3.10-venv ca-certificates ntpdate
ntpdate time.google.com
update-ca-certificates

cd /vagrant
python3 -m venv venv
/vagrant/venv/bin/pip install --upgrade pip setuptools wheel
/vagrant/venv/bin/pip install -r /vagrant/requirements.txt

# --- CONFIGURACIÓN DEL SERVICIO WEB ---
echo "--- Configurando el servicio web ---"
cp /vagrant/dns-shortener.service /etc/systemd/system/dns-shortener.service
systemctl daemon-reload
systemctl enable dns-shortener.service
systemctl start dns-shortener.service
echo "--- ¡El servicio web ha sido iniciado! ---"

# --- CONFIGURACIÓN DEL SINCRONIZADOR EN SEGUNDO PLANO (CRON) ---
echo "--- Configurando el sincronizador de DNS (cron) ---"
CRON_JOB="* * * * * vagrant /vagrant/venv/bin/python3 /vagrant/sync_dns.py >> /vagrant/cron.log 2>&1"
echo "$CRON_JOB" > /etc/cron.d/dns-sync
chmod 0644 /etc/cron.d/dns-sync
echo "--- ¡El sincronizador está configurado para ejecutarse cada minuto! ---"