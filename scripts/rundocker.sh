#!/bin/bash

if [ -z "$TRADE_DATA" ]; then
    echo environment variable TRADE_DATA is not set
    exit 1
fi

if [ ! -d "$TRADE_DATA" ]; then
    echo $TRADE_DATA should be a directory
    exit 1
fi

TMP_DIR=tmp/ext
mkdir -p $TMP_DIR
find "$TRADE_DATA" -maxdepth 1 \( -name '*csv' -o -name '*json' \) -print0 | while read -d $'\0' file
do
  cp "$file" $TMP_DIR
done

cp ~/.smartrade/*{json,yml} $TMP_DIR

env=${1-prod}
docker-compose -f docker-compose.yml -f docker-compose-${env}.yml up --build -d

rm -rf $TMP_DIR