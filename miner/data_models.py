import json
import subprocess
import requests
from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, Optional, Union
from substrateinterface.utils import ss58
from pathlib import Path
from fastapi import FastAPI, APIRouter


class Ss58Key:
    ss58_address: str
    folder_path: str
    
    def __init__(self, address: str, folder_path: str = "$HOME/.commune/key") -> None:
        super().__init__()
        self.ss58_address = self.add_address(address)
        self.folder_path = folder_path

        
    def add_address(self, key_info: str) -> str:
        if key_info.startswith("0x"):
            encoded_address = ss58.ss58_encode(key_info)
        if key_info.startswith("5"):
            encoded_address = key_info
        else:
            try:
                encoded_address = self.get_keyfile_path(key_info)["ss58_address"]
            except FileNotFoundError:
                encoded_address = ss58.ss58_encode(key_info)
        self.__setattr__("ss58_address", encoded_address)
        return encoded_address
        
    def encode(self, public_address: str) -> str:
        return ss58.ss58_encode(public_address)
                  
    def get_keyfile_path(self, key_name: str) -> str:
        with open(f"{self.folder_path}/{key_name}.json", "r", encoding="utf-8") as f:
            json_data = json.loads(f.read())['data']
            return json.loads(json_data)

    def __str__(self) -> str:
        return str(self.ss58_address)
    
    def __setattr__(self, name: str, value: Any) -> None:
        if name == "ss58_address":
            return super().__setattr__(name, value)
        return super().__setattr__(name, self.encode(value))

    def __hash__(self) -> int:
        return hash(self.ss58_address)
    
    def __get_pydantic_core_schema__(self, _config: ConfigDict) -> Dict[str, Any]:
        return {"ss58_address": str}
    

class MinerRequest(BaseModel):
    data: Optional[Dict[str, Any]]
    model: Optional[str]
    config: Optional[Dict[str, Any]]


class ModuleConfig(BaseModel):
    module_name: str
    module_path: str
    module_endpoint: str
    module_url: str
    

class BaseModule(BaseModel):
    module_settings: ModuleConfig
    
    def __init__(self, module_settings: ModuleConfig):
        self.init_module(module_settings)
        self.module_settings = module_settings
        
    def init_module(self, module_config: ModuleConfig):
        self.install_module(module_config)

    def get_module(self, module_config: ModuleConfig):
        return requests.get(module_config.module_url, timeout=30).text

    def save_module(self, module_config: ModuleConfig, module_data):
        with open(f"{module_config.module_path}/setup_{module_config.module_name}.py", "w", encoding="utf-8") as f:
            f.write(module_data)

    def setup_module(self, module_config: ModuleConfig):
        command = f"python {module_config.module_name}/setup_{module_config.module_name}.py"
        subprocess.run(command, shell=True, check=True)
        command = f"python {module_config.module_name}/install_{module_config.module_name}.sh"
        subprocess.run(command, shell=True, check=True)

    def update_module(self, module_config: ModuleConfig):
        self.install_module(module_config)

    # TODO Rename this here and in `init_module` and `update_module`
    def install_module(self, module_config):
        module_data = self.get_module(module_config)
        self.save_module(module_config, module_data)
        self.setup_module(module_config)
        
        
class MinerConfig(BaseModel):
    key_name: str
    key_folder_path: str
    host_address: str
    external_address: str
    port: int
    ss58_address: str
    use_testnet: bool
    module: BaseModule
    call_timeout: int
    miner_key_path: Optional[str] = None
