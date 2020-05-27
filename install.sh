#!/usr/bin/env bash

# Scripts
cp coast /usr/lib/coast
rm -r /usr/lib/coast # remove old version
chmod +x /usr/lib/coast/coast.py
ln /usr/lib/coast/coast /usr/bin/coast

# Requirements
python3 -m pip install -r coast/requirements.txt

# Config
cp -n coast.yml /etc/coast.yml
chown root:root /etc/coast.yml
chmod 600 /etc/coast

# Cron
cp coast.cron /etc/cron.d/coast
chmod +x /etc/cron.d/coast
service cron reload
