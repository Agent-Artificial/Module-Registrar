import argparse
import requests

from ..base_module import BaseModule
from .data_models import ModuleConfig, TranslationRequest
from seamless_communication.inference.translator import SeamlessTranslator
from typing import Any, Optional


class TranslateMiner(BaseModule):

    def __init__(self, module_config: Optional[ModuleConfig] = None):
        super().__init__()
        self.config = ModuleConfig(**module_config)
        self.translator = SeamlessTranslator()

    def process(self, url: str, request: TranslationRequest) -> Any:
        """Process a request made to the module."""
        if request.inference_type == "translation":
            result = self.translator.translation_inference(in_file=request.request_data.in_file, task_string=request.request_data.task_string, target_languages=request.request_data.target_language)
        
        print(result)
    
        
    
        
        
        



def parse_arugments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keyname", type=str, default="eden.Miner_2")
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    return parser.parse_args()



if __name__ == "__main__":

    args = parse_arugments()
    miner = TranslateMiner()

    miner.start_miner_server(args.keyname, args.host, args.port)