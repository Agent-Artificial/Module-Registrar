import base64
import os
import wave


class AudioManager:
    def __init__(self):
        self.input_path = "module_registrar/modules/whisper/in/audio_request.wav"
        self.output_path = "module_registrar/modules/whisper/out/audio_request.wav"

    def encode_audio(self, audio_path):
        """Encode audio file to base64 string."""
        with open(audio_path, "rb") as audio_file:
            audio_content = audio_file.read()
        return self.encode_processed_data(audio_content)
    
    def decode_audio(self, base64_string):
        """Decode base64 string to audio data."""
        return self.decode_processed_data(base64_string)

    def save_audio(self, base64_string):
        """Decode and save base64 audio string to input path."""
        audio_data = self.decode_audio(base64_string)
        os.makedirs(os.path.dirname(self.input_path), exist_ok=True)
        wave_file = wave.open(self.input_path, 'wb')
        wave_file.setnchannels(1)
        wave_file.setsampwidth(2)  # 16-bit
        wave_file.setframerate(16000)  # 16kHz
        wave_file.writeframes(audio_data)
        wave_file.close()
            
    def retrieve_processed_data(self):
        """Retrieve processed data from output path."""
        if not os.path.exists(self.output_path):
            return None
        with open(self.output_path, 'rb') as file:
            return file.read()

    def encode_processed_data(self, data):
        """Encode processed data to base64 string."""
        return base64.b64encode(data.encode('utf-8')).decode('utf-8')

    def decode_processed_data(self, base64_string):
        """Decode base64 string to processed data."""
        return base64.b64decode(base64_string).decode('utf-8')