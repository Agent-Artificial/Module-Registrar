import os
import argparse
import requests
import torch
from pydantic import BaseModel, ConfigDict

from .data_models import TranslationRequest, TranslationConfig, MinerRequest, BaseModule, ModuleConfig, BaseMiner, MinerConfig, router
from .translation import SeamlessTranslator
from typing import Any, Optional
from dotenv import load_dotenv

load_dotenv()

translation_settings = TranslationConfig()
translation_settings.module = SeamlessTranslator()
miner_settings = MinerConfig()


class TranslationMiner(BaseMiner):
    module_config: MinerConfig
    module: BaseModule
    router: Any
    
    def __init__(self, module_config: Optional[TranslationConfig] = None):
        super().__init__(
            config=module_config, 
            router=router
            )
        self.module_config = module_config
        self.module = module_config.module
        self.router = router
        self.key_name = module_config.key_name
        self.key_folder_path = module_config.key_folder_path
        self.host_address = module_config.host_address
        self.external_address = module_config.external_address
        self.call_timeout = module_config.call_timeout
        self.miner_keypath = module_config.miner_key_path
        self.port = module_config.port
        self.ss58_address = module_config.ss58_address
        self.use_testnet = module_config.use_testnet

    def process(self, request: TranslationRequest) -> Any:
        """Process a request made to the module."""
        if request.inference_type == "translation":
            return self.module.translation_inference(
                in_file=request.request_data.in_file,
                task_string=request.request_data.task_string,
                target_languages=request.request_data.target_language,
            )
    
    
if __name__ == "__main__":
    miner = TranslationMiner(
        module_config=translation_settings
        )

    miner.start_miner_server(translation_settings.host_address, translation_settings.port)