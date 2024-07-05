#!/bin/bash

# Install whisper.cpp
git clone https://github.com/ggerganov/whisper.cpp.git module_registrar/modules/whisper/whisper.cpp
cd module_registrar/modules/whisper/whisper.cpp
make clean
WHISPER_CBLAST=1 make -j

# Download Whisper model
bash models/download-ggml-model.sh base.en
    
# Make in and out dirs
cd .. 
mkdir -p in out

cd ../../..

# Run example
bash module_registrar/modules/whisper/example.sh
