#!/bin/bash

set -e

LOG_DIR="%(DEPLOY_DIR)s/logs"
LOG_FILE="$LOG_DIR/celery.log"

test -d "$LOG_DIR" || mkdir -p "$LOG_DIR"
cd "%(DEPLOY_DIR)s"

source %(ENV_PATH)s/bin/activate
source %(ENV_PATH)s/bin/postactivate
export DJANGO_SETTINGS_MODULE="%(SETTINGS_MODULE)s"

exec celery -A dpix_io worker -E -c 3 --loglevel=DEBUG --logfile="$LOG_FILE"
