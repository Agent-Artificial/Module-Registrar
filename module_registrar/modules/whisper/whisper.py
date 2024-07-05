import argparse
import subprocess
from pathlib import Path

from loguru import logger

def run_whisper(
    whisper_bin="module_registrar/modules/whisper/whisper.cpp/main",
    file_path="module_registrar/modules/whisper/in/jfk.wav",
    model_path="module_registrar/modules/whisper/whisper.cpp/models/ggml-base.en.bin",
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
        "-f", "--file_path", default="module_registrar/modules/whisper/input/jfk.wav", type=str, required=False
    )
    parser.add_argument(
        "-m",
        "--model_path",
        default="module_registrar/modules/whisper/whisper.cpp/models/ggml-base.en.bin",
        type=str,
        required=False,
    )
    parser.add_argument("-w", "--whisper_bin", default="module_registrar/modules/whisper/whisper.cpp/main", type=str)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    run_whisper(**vars(args))
