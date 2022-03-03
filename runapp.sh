env=${1-d}
if [[ $env == p* ]]; then
    env=production
    port=5000
else
    env=development
    port=5001
fi
FLASK_APP=smartrade FLASK_ENV=$env FLASK_RUN_PORT=$port FLASK_RUN_HOST=0.0.0.0 FLASK_CONF_PATH=~/.smartrade/config.yml flask run
