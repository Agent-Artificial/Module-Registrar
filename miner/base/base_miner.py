import os
import json
from pathlib import Path
from loguru import logger
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from communex.client import CommuneClient
from communex._common import get_node_url
from communex.compat.key import Keypair
from data_models import MinerRequest
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

class MinerConfig(BaseModel):
    module_config: ModuleConfig = Field(default_factory=ModuleConfig)
    miner_key_dict: Dict[str, Any] = Field(default_factory=dict)
    key_name: str = Field(default="test_miner_1")

class BaseMiner(ABC):
    module_config: ModuleConfig = Field(default_factory=ModuleConfig)
    miner_key_dict: Dict[str, Any] = Field(default_factory=dict)
    key_name: str = Field(default="test_miner_1")
    def __init__(self, module_config: ModuleConfig, miner_config: MinerConfig):
        self.module_config = module_config
        self.miner_config = miner_config
        self.router = APIRouter()

    def add_route(self, module_name: str):
        @self.router.post(f"/modules/{module_name}/process")
        def process_request(request: MinerRequest):
            return self.process(request)
        app.include_router(self.router)

    @staticmethod
    def run_server(host_address: str, port: int):
        import uvicorn
        uvicorn.run(app, host=host_address, port=port)

    @staticmethod
    def get_miner_keys(keypath: Optional[str] = None):
        keypath = keypath or os.getenv("MINER_KEYPATH")
        return json.loads(Path(keypath).read_text(encoding="utf-8"))

    def add_miner_key(self, key_name: str, miner_keypath: Path = Path("data/miner_keys.json")):
        self.miner_key_dict[key_name] = MinerConfig().model_dump()
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

    def register_miner(self, key_name: str, external_address: str, port: int, subnet: str, min_stake: int, metadata: str):
        address = f"{external_address}:{port}"
        keypair = self.get_keypair(key_name)
        result = comx.register_module(keypair, key_name, address, subnet, min_stake, metadata)
        return result.extrinsic

    def serve_miner(
        self,
        module_name: str, 
        key_name: str, 
        host_address: str, 
        external_address: str,
        port: int,
        subnet: str,
        min_stake: int,
        metadata: str,
        register: bool = False
    ):
        self.add_route(module_name)
        if register:
            self.register_miner(key_name, external_address, port, subnet, min_stake, metadata)
            logger.info(f"Registered {key_name} at {external_address}:{port}")
        self.run_server(host_address, port)

    @abstractmethod
    def process(self, miner_request: MinerRequest) -> Any:
        """Process a request made to the module."""