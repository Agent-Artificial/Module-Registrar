#!/bin/bash

set -e

# Update apt
apt-get update && apt-get upgrade -y

# Install dependencies
apt-get install -y python3.10 python3-pip build-essential libssl-dev libffi-dev python3-dev python3-venv python3-setuptools python3-pip wget curl libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libxslt1.1 libxslt1-dev libxml2 libxml2-dev python-is-python3 libpugixml-dev libtbb-dev git git-lfs ffmpeg libclblast-dev cmake make

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Update pip
python -m pip install --upgrade pip
pip install wheel setuptools
pip install loguru

python -m pip install -r requirements.txt

whisper() {
    python eden_bittensor_subnet/modules/whisper/setup_whisper.py
}

read -p "Do you want to install Whisper? (y/n) " -n 1 -r

if [[ $REPLY =~ ^[Yy]$ ]]
then
    whisper
fi