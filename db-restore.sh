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
declare -r HELP_MSG="Usage: $SCRIPT_NAME database
  -n       new database
  -h       display this help and exit
  -d       date
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

while getopts ":d:hn:" opt; do
    case $opt in
        h)
            usage 0
            ;;
        d)
            date=${OPTARG}
            ;;
        n)
            new_db=${OPTARG}
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

if [[ -z "$new_db" ]]; then
    new_db=$db
fi

mongorestore --db $new_db --drop $data_dir/$db
