#!/bin/sh

if [ $# -lt 3 ]; then
  echo "Usage: $0 --schedule '<cron_schedule>' <command>"
  exit 1
fi

SCHEDULE=$2
shift 2
COMMAND=$@

echo "$SCHEDULE $COMMAND >> /var/log/cron.log 2>&1" > /etc/cron.d/cron-job

chmod 0644 /etc/cron.d/cron-job

crontab /etc/cron.d/cron-job

echo "Starting cron with schedule: '$SCHEDULE' and command: '$COMMAND'"
cron -f
