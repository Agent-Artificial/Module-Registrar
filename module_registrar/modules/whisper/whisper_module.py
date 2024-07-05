import base64
import ffmpeg

from module_registrar.modules.base_module import BaseModule
from module_registrar.modules.whisper.whisper import run_whisper
from module_registrar.modules.whisper.convert_file import convert_to_wav
from module_registrar.modules.whisper.setup.audio_manager import AudioManager


class WhisperModule(BaseModule):
    def __init__(self):
        super().__init__()
        self.audio = AudioManager()
        
    async def process(self, base64_request: str) -> str:
        self.audio.save_audio(base64_request)
        convert_to_wav("module_registrar/modules/whisper/in/input.wav")
        run_whisper(
            whisper_bin="module_registrar/modules/whisper/whisper.cpp/main",
            file_path="module_registrar/modules/whisper/out/output.wav",
            model_path="module_registrar/modules/whisper/whisper.cpp/models/ggml-base.en.bin"
        )
        data = self.audio.retrieve_processed_data()
        return self.audio.encode_processed_data(data)
        
        