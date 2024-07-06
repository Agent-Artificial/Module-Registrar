#!/bin/bash

set -e

source ./.venv/bin/activate
source .env

read -p "Enter miner name: " MINER_NAME
read -P "Enter keyfile name: " KEYPATH_NAME
read -p "Enter miner host: " MINER_HOST
read -p "Enter miner port: " MINER_PORT
read -p "Enter miner stake: " STAKE
read -p "Enter netuid: " NETUID

if [ ! -f "$KEY_PATH"/"$KEYPATH_NAME" ]; then
echo "Creating key"
comx key create "$KEYPATH_NAME"
fi

read -p "Register miner? [y/n] " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    comx register "$MINER_NAME" "$KEYPATH_NAME" --host "$MINER_HOST" --port "$MINER_PORT" --stake "$STAKE" --netuid "$NETUID"
fi

