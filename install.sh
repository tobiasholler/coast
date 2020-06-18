#!/usr/bin/env bash

# check for root
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Checking requirements
command -v docker || (>&2 echo "Docker must be installed for AWS Backup to work!"; exit 1)

# Pulling AWS CLI
docker pull amazon/aws-cli

# Scripts
rm -rf /usr/lib/coast # remove old version
cp -r coast /usr/lib/coast
chmod +x /usr/lib/coast/coast.py
ln -s /usr/lib/coast/coast.py /usr/bin/coast

# Requirements
python3 -m pip install -r coast/requirements.txt

# Config
cp -n coast.yml /etc/coast.yml
chown root:root /etc/coast.yml
chmod 600 /etc/coast.yml

# Creating Log Folder
mkdir -p /var/log/coast

# Cron
cp coast.cron /etc/cron.d/coast
chmod +x /etc/cron.d/coast
service cron reload

echo "Coast installed.\nRun 'coast --aws-configure' to configure AWS."
