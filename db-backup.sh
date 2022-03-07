#!/bin/bash

[[ -n "$MONGODB_DATA" ]] || { echo "environment variable MONGODB_DATA not set"; exit 2; }

dir=$MONGODB_DATA/backups

[ -d "$dir" ] || { echo "backup directory $dir doesn't exist"; exit 2; }

db=${1-d}
if [[ $db == p* ]]; then
    db=trading_prod
elif [[ $db == d* ]]; then
    db=trading_dev
else
    db=trading_test
fi

db_dir=$dir/`date +"%m-%d-%y"`
echo backup database $db to $db_dir...
mongodump --db $db --out  $db_dir
