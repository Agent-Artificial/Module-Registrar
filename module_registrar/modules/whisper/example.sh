#! /bin/bash

cp module_registrar/modules/whisper/whisper.cpp/samples/jfk.wav module_registrar/modules/whisper/in

python module_registrar/modules/whisper/convert_file.py -f module_registrar/modules/whisper/in/jfk.wav

python module_registrar/modules/whisper/whisper.py -f module_registrar/modules/whisper/in/jfk.wav -m module_registrar/modules/whisper/whisper.cpp/models/ggml-base.en.bin -w module_registrar/modules/whisper/whisper.cpp/main
