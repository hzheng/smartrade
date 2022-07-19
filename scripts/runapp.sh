#!/bin/bash

env=${1-d}
if [[ $env == p* ]]; then
    env=production
    build='build'
    port=5000
else
    env=development
    build='watch'
    port=5001
fi

#npx babel --watch smartrade/static/jsx --out-dir smartrade/static/generated --presets react-app/prod &
eval "NODE_ENV=$env npm run --prefix smartrade/static $build" &

vars="FLASK_APP=smartrade FLASK_ENV=$env FLASK_RUN_PORT=$port FLASK_RUN_HOST=0.0.0.0 FLASK_CONF_PATH=~/.smartrade/config.yml"
timeout=${2-0}

if [ "$timeout" -eq "0" ]; then
    eval "$vars flask run"
else
    eval "$vars gunicorn --timeout $timeout -w 1 -b 0.0.0.0:$port smartrade.wsgi:app"
fi

