FLASK_APP=smartrade FLASK_ENV=${1-development} FLASK_RUN_PORT=5000 FLASK_RUN_HOST=0.0.0.0 FLASK_CONF_PATH=~/.smartrade/config.yml flask run
