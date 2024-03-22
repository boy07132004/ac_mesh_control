#!/bin/bash
printenv > /etc/environment && chmod 755 /code/cron_script && crontab /code/cron_script && cron start
cd /code
uvicorn main:app --host 0.0.0.0 --port 8000
