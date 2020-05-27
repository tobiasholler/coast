#!/usr/bin/env python3
import os
import subprocess
import sys
from datetime import datetime

import yaml
import argparse
import logging

LOG_FORMAT = '[%(asctime)s] %(levelname)s: \t%(message)s'

log = logging.getLogger()
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.NOTSET)
formatter = logging.Formatter(LOG_FORMAT)
handler.setFormatter(formatter)
log.addHandler(handler)

parser = argparse.ArgumentParser(description="Coast Backup Tool")
parser.add_argument("--backup-now", action="store_true")
parser.add_argument("--dry-run", action="store_true")
parser.add_argument("--config-check", action="store_true")
parser.add_argument("--config-file", default="/etc/coast.yml")
args = parser.parse_args()

log.info(f"Reading config file \"{args.config_file}\"")
config_file = open(args.config_file, "r")
config = yaml.load(config_file, Loader=yaml.FullLoader)
config_file.close()

# Setting Loglevel set in config file
log.setLevel(config["log_level"] if "log_level" in config else log.setLevel(logging.DEBUG))

# check config

base_backup_dir = config["base_backup_dir"] if "base_backup_dir" in config else "/opt/coast_backups/"

if args.backup_now:
  directories = config["directories"]
  logging.info(f"Directories to back up: {list(directories.keys())}")
  for name in directories:
    directory = directories[name]
    handler.setFormatter(logging.Formatter(f"[%(asctime)s] %(levelname)s: \t({name})\t%(message)s"))
    logging.info(f"Backing up \"{name}\"")
    backup_dir = directory["backup_dir"] if "backup_dir" in directory else os.path.join(base_backup_dir, name)
    source_dir = directory["source_dir"]
    logging.info(f"From: \"{source_dir}\"")
    logging.info(f"To: \"{backup_dir}\"")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    target_file = os.path.join(backup_dir, f"{name}_incremental_backup_{timestamp}.tar.gz")
    snapshot_file = os.path.join(backup_dir, f"{name}_incremental_backup.tar.snapshot")
    def d(f):
      if not args.dry_run:
        f()
      else:
        log.warning("Not called because of dry run!")
    if "pre_backup_command" in directory:
      log.info(f"Calling pre backup command \"{directory['pre_backup_command']}\" in \"{source_dir}\"")
      d(lambda: os.system(f"cd {source_dir} && {directory['pre_backup_command']}"))
    log.debug("Creating nessecary directories")
    d(lambda: subprocess.call(["mkdir", "-p", backup_dir]))
    backup_command = ["tar", "-czf", target_file, f"--listed-incremental={snapshot_file}", source_dir]
    log.info(f"Calling backup command \"{' '.join(backup_command)}\"")
    d(lambda: subprocess.call(backup_command))
    if "post_backup_command" in directory:
      log.info(f"Calling post backup command \"{directory['post_backup_command']}\" in \"{source_dir}\"")
      d(lambda: os.system(f"cd {source_dir} && {directory['post_backup_command']}"))
    # encryption
    if "encryption_password" in directory:
      encryption_password = directory["encryption_password"]
      target_file_enc = target_file + ".enc"
      log.info(f"Encrypting \"{target_file}\" to \"{target_file_enc}\" with AES-256-cbc")
      encryption_command = ["openssl", "enc", "-aes-256-cbc", "-in", target_file, "-k", str(encryption_password), "-md", "sha1", "-pbkdf2"]
      log.debug(f"Encryption command: {encryption_command}")
      f = open(target_file_enc, "wb")
      process = subprocess.run(encryption_command, stdout=subprocess.PIPE)
      f.write(process.stdout)
      f.close()
      log.info(f"Encryption finished")