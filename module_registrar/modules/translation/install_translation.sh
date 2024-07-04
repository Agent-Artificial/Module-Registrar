#!bin/bash

set -e

source ./.venv/bin/activate

python -m pip install --upgrade pip

pip install setuptools wheel gnureadline
pip install sndfile ggml-python

sudo apt-get libsndfile1-dev

git clone https://github.com/facebookresearch/seamless_communication.git ./module_registrar/modules/translation/seamless

pip install ./module_registrar/modules/translation/seamless

pip install git+https://github.com/huggingface/transformers torch torchaudio torchvision fairseq2

mkdir -p /module_registrar/modules/translation/in

mkdir -p /module_registrar/modules/translation/out

