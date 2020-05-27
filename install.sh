#!/usr/bin/env bash

# Scripts
cp coast /usr/lib/coast
chmod +x /usr/lib/coast/coast
ln /usr/lib/coast/coast /usr/bin/coast

# Requirements
python3 -m pip install -r coast/requirements.txt

# Config
cp coast.yml /etc/coast.yml

# Cron
cp coast.cron /etc/cron.d/coast
chmod +x /etc/cron.d/coast
service cron reload
