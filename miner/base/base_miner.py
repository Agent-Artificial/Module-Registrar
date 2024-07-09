import os
import json
import subprocess
from pathlib import Path
from loguru import logger
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, List
from pydantic import BaseModel, Field
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from communex.client import CommuneClient
from communex._common import get_node_url
from communex.compat.key import Keypair
from base.base_module import ModuleConfig

# Initialize CommuneClient
comx = CommuneClient(get_node_url())

# FastAPI setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MinerRequest(BaseModel):
    data: Any = Field(default=None)
    

class MinerConfig(BaseModel):
    miner_name: Optional[str] = None
    miner_keypath: Optional[str] = None
    miner_host: Optional[str] = None
    external_address: Optional[str] = None
    miner_port: Optional[int] = None
    stake: Optional[float] = None
    netuid: Optional[int] = None
    funding_key: Optional[str] = None
    funding_modifier: Optional[float] = None
    module_name: Optional[str] = None


class BaseMiner(ABC):
    module_config: ModuleConfig = Field(default_factory=ModuleConfig)
    module_configs: List[MinerConfig] = Field(default_factory=list)
    miner_key_dict: Dict[str, Any] = Field(default_factory=dict)
    key_name: str = Field(default="test_miner_1")
    
    def __init__(self, module_config: ModuleConfig, miner_config: MinerConfig):
        self.module_config = module_config
        self.module_configs = self.get_module_configs()
        self.miner_config = miner_config
        self.miner_configs = self.get_miner_configs()
        self.miners = self.get_miner_keys(self.miner_configs)
        self.router = APIRouter()

    def get_miner_configs(self):
        if os.path.exists("modules/miner_configs.json"):
            with open("modules/miner_configs.json", "r", encoding="utf-8") as f:
                return json.loads(f.read())
        else:
            with open("modules/miner_configs.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(self.miner_configs, indent=4))
        return self.miner_configs
    
    def get_module_configs(self):
        if os.path.exists("modules/module_configs.json"):
            with open("modules/module_configs.json", "r", encoding="utf-8") as f:
                return json.loads(f.read())
        else:
            with open("modules/module_configs.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(self.module_configs, indent=4))
        return self.module_configs
        
    def add_route(self, module_name: str):
        @self.router.post(f"/modules/{module_name}/process")
        def process_request(request: MinerRequest):
            return self.process(request)
        app.include_router(self.router)

    @staticmethod
    def run_server(host_address: str, port: int):
        import uvicorn
        uvicorn.run(app, host=host_address, port=port)

    def get_miner_keys(self, miner_configs: List[MinerConfig]):
        key_path = Path("data/instance_data/miner_keys.json")
        if os.path.exists("data/instance_data/miner_keys.json"):
            return json.loads(key_path.read_text(encoding="utf-8"))
        keypaths = [config["miner_keypath"] for config in miner_configs]
        grabbed_paths = []
        for keypath in keypaths:
            if keypath not in grabbed_paths:
                keypath = Path(keypath)
                key_data = json.loads(keypath.read_text(encoding="utf-8"))
                self.miner_key_dict[key_data["name"]] = key_data

        key_path.write_text(json.dumps(self.miner_key_dict, indent=4), encoding="utf-8")
        return self.miner_key_dict
    
    def add_miner_key(self, key_name: str, miner_keypath: Path = Path("data/instance_data/miner_keys.json"), miner_config: Optional[MinerConfig] = None):
        if miner_config:
            self.miner_config[key_name] = miner_config.model_dump()
        else:
            print("Configuring miner: ")
            miner_name = input("Enter miner_name ")
            miner_keypath = input("Enter miner_keypath [ex. $HOME/.commune/key/my_miner.json]: ", None)
            miner_host = input("Enter miner_host [default 0.0.0.0]:", "0.0.0.0")
            external_address = input("Enter external_address: ", None)
            miner_port = input("Enter miner_port [default 5757]: ", 5757)
            stake = input("Enter stake [default 275COM]: ", 275)
            netuid = input("Enter netuid [default 0]: ", 0)
            funding_key = input("Enter funding_key: ")
            modifier = input("Enter modifier [default 15COM]: ")
            module_config = ModuleConfig(
                miner_name=miner_name,
                miner_keypath=miner_keypath,
                miner_host=miner_host,
                external_address=external_address,
                miner_port=miner_port,
                stake=stake,
                netuid=netuid,
                funding_key=funding_key,
                funding_modifier=modifier,
                
            )

            self.miner_config[key_name] = module_config.model_dump()
        
        self._save_miner_keys(miner_keypath)

    def remove_miner_key(self, key_name: str, miner_keypath: Path):
        self.miner_key_dict.pop(key_name, None)
        self._save_miner_keys(miner_keypath)

    def update_miner_key(self, key_name: str, miner_config: MinerConfig, miner_keypath: Path):
        self.miner_key_dict[key_name] = miner_config.model_dump()
        self._save_miner_keys(miner_keypath)

    def _save_miner_keys(self, miner_keypath: Path):
        miner_keypath.write_text(json.dumps(self.miner_key_dict), encoding="utf-8")

    def load_miner_keys(self, miner_keypath: Path):
        self.miner_key_dict = json.loads(miner_keypath.read_text(encoding="utf-8"))

    def get_keypair(self, key_name: str):
        key_folder_path = Path(self.module_config.key_folder_path)
        json_data = json.loads((key_folder_path / f"{key_name}.json").read_text(encoding='utf-8'))["data"]
        key_data = json.loads(json_data)
        return Keypair(key_data["private_key"], key_data["public_key"], key_data["ss58_address"])

    def register_miner(self, miner_config: MinerConfig):
        command = f"bash modules/setup_miners.sh {miner_config.miner_name} {miner_config.miner_keypath} {miner_config.external_address} {miner_config.miner_port} {miner_config.stake} {miner_config.netuid} {miner_config.funding_key} {miner_config.modifier}"
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info(result.stdout.decode("utf-8"))
        logger.info(result.stderr.decode("utf-8"))
        
    def serve_miner(
        self,
        miner_config: MinerConfig,
        register: bool = False
    ):
        self.add_route(miner_config.module_name)
        if register:
            self.register_miner(miner_config)
            logger.info(f"Registered {miner_config.key_name} at {miner_config.external_address}:{miner_config.port}")
        self.run_server(miner_config.host_address, miner_config.port)

    @abstractmethod
    def process(self, miner_request: MinerRequest) -> Any:
        """Process a request made to the module."""