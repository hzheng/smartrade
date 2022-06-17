#!/bin/bash

env=${1-d}
if [[ $env == p* ]]; then
    env=production
    port=5000
else
    env=development
    port=5001
fi

vars="FLASK_APP=smartrade FLASK_ENV=$env FLASK_RUN_PORT=$port FLASK_RUN_HOST=0.0.0.0 FLASK_CONF_PATH=~/.smartrade/config.yml"
timeout=${2-0}

if [ "$timeout" -eq "0" ]; then
    eval "$vars flask run"
else
    eval "$vars gunicorn --timeout $timeout -w 1 -b 0.0.0.0:$port smartrade.wsgi:app"
fi
