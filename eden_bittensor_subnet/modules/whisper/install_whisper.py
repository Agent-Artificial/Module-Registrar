import os
import subprocess
import json
from pathlib import Path

subprocess.run(["pip", "install", "loguru"], check=True)

from loguru import logger

def install_cuda():
    commands = """
#!/bin/bash
# Install CUDA
pip install nvidia-pyindex
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/12.3.0/local_installers/cuda-repo-ubuntu2204-12-3-local_12.3.0-545.23.06-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2204-12-3-local_12.3.0-545.23.06-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2204-12-3-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-3
"""
    cuda = input("Do you want to install CUDA 12.3? (y/n): ")
    cuda = cuda in ["y", "Y", "yes", "Yes"]
    if cuda:
        subprocess.run([commands], check=True, shell=True)
    return cuda
    
install_cuda()

install_whisper_sh = """#!/bin/bash

# Install whisper.cpp
git clone https://github.com/ggerganov/whisper.cpp.git eden_bittensor_subnet/modules/whisper/whisper.cpp
cd eden_bittensor_subnet/modules/whisper/whisper.cpp
make clean
WHISPER_CBLAST=1 make -j

# Download Whisper model
bash models/download-ggml-model.sh base.en
    
# Make in and out dirs
cd .. 
mkdir -p in out

cd ../../..

# Run example
bash eden_bittensor_subnet/modules/whisper/example.sh
"""
example_sh = """#! /bin/bash

cp eden_bittensor_subnet/modules/whisper/whisper.cpp/samples/jfk.wav eden_bittensor_subnet/modules/whisper/in

python eden_bittensor_subnet/modules/whisper/convert_file.py -f eden_bittensor_subnet/modules/whisper/in/jfk.wav

python eden_bittensor_subnet/modules/whisper/whisper.py -f eden_bittensor_subnet/modules/whisper/in/jfk.wav -m eden_bittensor_subnet/modules/whisper/whisper.cpp/models/ggml-base.en.bin -w eden_bittensor_subnet/modules/whisper/whisper.cpp/main
"""

convert_file_py = """import argparse
import subprocess
from pathlib import Path



def convert_to_wav(file_path):
    input_name = Path(file_path)
    output_name = input_name.name.format("wav")
    output_path = Path(f"eden_bittensor_subnet/modules/whisper/out/{output_name}")
    subprocess.run(
        [
            "ffmpeg",
            "-i",
            f"{input_name}",
            "-ar",
            "16000",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            f"{output_path}",
        ],
        check=True,
    )


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file_path", type=str, required=True)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    file_path = parse_args().file_path
    convert_to_wav(file_path)
"""

whisper_py = """import argparse
import subprocess
from pathlib import Path

from loguru import logger

def run_whisper(
    whisper_bin="eden_bittensor_subnet/modules/whisper/whisper.cpp/main",
    file_path="eden_bittensor_subnet/modules/whisper/in/jfk.wav",
    model_path="eden_bittensor_subnet/modules/whisper/whisper.cpp/models/ggml-base.en.bin",
):
    file_path = Path(file_path)
    model_path = Path(model_path)
    whisper_path = Path(whisper_bin)
    try:
        result = subprocess.run(
            [f"{whisper_bin}", "-m", f"{model_path}", "-f", f"{file_path}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        logger.debug(result.stdout.decode("utf-8"))
        return result.stdout.decode("utf-8")
    except subprocess.CalledProcessError as error:
        logger.error(error)
        return error
    except RuntimeError as error:
        logger.error(error)
        return error


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--file_path", default="eden_bittensor_subnet/modules/whisper/input/jfk.wav", type=str, required=False
    )
    parser.add_argument(
        "-m",
        "--model_path",
        default="eden_bittensor_subnet/modules/whisper/whisper.cpp/models/ggml-base.en.bin",
        type=str,
        required=False,
    )
    parser.add_argument("-w", "--whisper_bin", default="eden_bittensor_subnet/modules/whisper/whisper.cpp/main", type=str)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    run_whisper(**vars(args))
"""

inference_types = Path("eden_bittensor_subnet/modules/inference_types.json")

type_data = "whisper"
json_data = {"type": []}
if os.path.exists(inference_types):
    json_data = json.loads(inference_types.read_text())
json_data["type"].append(type_data)
inference_types.write_text(json.dumps(json_data))


file_paths = {
    "install_whisper_sh": Path("eden_bittensor_subnet/modules/whisper/install_whisper.sh"),
    "example_sh": Path("eden_bittensor_subnet/modules/whisper/example.sh"),
    "convert_file_py": Path("eden_bittensor_subnet/modules/whisper/convert_file.py"),
    "whisper_py": Path("eden_bittensor_subnet/modules/whisper/whisper.py")
}
data = {
    "install_whisper_sh": install_whisper_sh,
    "example_sh": example_sh,
    "convert_file_py": convert_file_py,
    "whisper_py": whisper_py
}

def write_file(file_data: str, file_path: str) -> None:
    logger.debug(f"\\nfile_data: {file_data}\\nfile_path: {file_path}\\n")
    file_path.write_text(file_data)
    file_path.chmod(0o777)


for key in file_paths.keys():
    write_file(data[key], file_paths[key])
    logger.debug(f"\\nfile: {file_paths[key]}\\n")

subprocess.run(["bash", "eden_bittensor_subnet/modules/whisper/install_whisper.sh"], check=True)