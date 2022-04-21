#!/bin/bash

[[ -n "$MONGODB_DATA" ]] || { echo "environment variable MONGODB_DATA not set"; exit 2; }

dir=$MONGODB_DATA/backups

[ -d "$dir" ] || { echo "backup directory $dir doesn't exist"; exit 2; }

declare -r SCRIPT_NAME=$(basename "$BASH_SOURCE" .sh)

## exit the shell(default status code: 1) after printing the message to stderr
bail() {
    echo -ne "$1" >&2
    exit ${2-1}
} 

## help message
declare -r HELP_MSG="Usage: $SCRIPT_NAME [-d date] [-H host] [-i ip] [database]
  -d       date
  -h       display this help and exit
  -H       source host
  -i       source ip
"

## print the usage and exit the shell(default status code: 2)
usage() {
    declare status=2
    if [[ "$1" =~ ^[0-9]+$ ]]; then
        status=$1
        shift
    fi
    bail "${1}$HELP_MSG" $status
}

while getopts ":d:hH:i:" opt; do
    case $opt in
        h)
            usage 0
            ;;
        d)
            date=${OPTARG}
            ;;
        i)
            ip=${OPTARG}
            ;;
        H)
            host=${OPTARG}
            ;;
        \?)
            usage "Invalid option: -$OPTARG \n"
            ;;
    esac
done

shift $(($OPTIND - 1))

#==========MAIN CODE BELOW==========

if [[ -z "$date" ]]; then
    date=`date +"%m-%d-%y"`
fi

data_dir=$dir/$date

db=${1-trading_prod}

if [[ -n "$host" ]]; then
    host=${host}:${ip-27019}
    uri="--uri=mongodb://smartrade:smartradeProd@$host/?authSource=admin"
else
    host=localhost:27017
fi

echo backup database $db on $host to $data_dir...

mongodump $uri --db $db --out $data_dir
