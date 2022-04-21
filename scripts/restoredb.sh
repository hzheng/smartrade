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
declare -r HELP_MSG="Usage: $SCRIPT_NAME [-n database] [-d date] [-H host] [-i ip] database
  -d       date
  -h       display this help and exit
  -H       target host
  -i       target ip
  -n       new database
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

while getopts ":d:hH:i:n:" opt; do
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
        n)
            new_db=${OPTARG}
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
[[ "$#" -ne 1 ]] && usage "Too few arguments\n"

#==========MAIN CODE BELOW==========

if [[ -z "$date" ]]; then
    date=`date +"%m-%d-%y"`
fi

data_dir=$dir/$date
[ -d "$data_dir" ] || { echo "backup directory $data_dir doesn't exist"; exit 2; }

db=$1

if [[ -n "$host" ]]; then
    uri="--uri=mongodb://smartrade:smartradeProd@${host}:${ip-27019}/?authSource=admin"
    if [[ -z "$new_db" ]]; then
        new_db=trading_prod
    fi
fi

if [[ -z "$new_db" ]]; then
    new_db=$db
fi

echo restore database $new_db from $data_dir/$db...

mongorestore $uri --db $new_db --drop $data_dir/$db
