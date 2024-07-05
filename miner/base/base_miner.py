import json
import uvicorn
from pathlib import Path
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import Dict, List, Union, Optional, Any
from ..data_models import Ss58Key, ModuleConfig, MinerConfig, BaseModule, MinerRequest
from importlib import import_module
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from communex.client import CommuneClient
from communex._common import get_node_url
from communex.compat.key import Keypair
from encryption import (
)


comx = CommuneClient(get_node_url())

embedding_router = APIRouter()


class BaseMiner(BaseModel, ABC):
    key_name: str
    key_folder_path: str
    host_address: str
    external_address: str
    port: int
    ss58_address: Optional[str]
    use_testnet: bool
    module: BaseModule
    call_timeout: int
    miner_keypath: Optional[str]
    miner_key_dict: Dict[str, str]
    __pydantic_fields_set__ = {"key_name", "key_folder_path", "host_address", "external_address", "port", "ss58_address", "use_testnet", "module", "call_timeout"}
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, settings: MinerConfig, config: ModuleConfig, router: APIRouter):
        super().__init__(module_config=config)
        self.init_module(settings)

    def init_module(self, module_config: ModuleConfig):
        self.install_module(module_config)
        

    def init_api(self, host_address: str, port: int, router: APIRouter):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.app.add_route("api/v1/process/{key_name}", router)
                
        self.server(
            host_address=host_address,
            port=port
        )

    def server(self, host_address: str, port: int):
        uvicorn.run(self.app, host=host_address, port=port)
        
    def get_miner_keys(self, key_folder: str):
        keypath = Path(key_folder).expanduser().resolve(strict=True) or self.miner_keypath
        return json.loads(keypath.read_text(encoding="utf-8"))        
    
    def add_miner_key(
        self,
        key_name: str,
        key_folder_path: str,
        host_address: str,
        external_address: str,
        port: int,
        ss58_address: Optional[str] = None,
        use_testnet: bool = False,
        call_timeout: int = 30,
        miner_keypath: Optional[str] = None
    ):
        miner_config = MinerConfig(
            key_name=key_name,
            key_folder_path=key_folder_path,
            host_address=host_address,
            external_address=external_address,
            port=port,
            ss58_address=ss58_address,
            use_testnet=use_testnet,
            call_timeout=call_timeout,
            miner_key_path=miner_keypath
        ).model_dump()
        self.miner_key_dict[key_name] = miner_config  
        self.miner_keypath.write_text(json.dumps(self.miner_key_dict), encoding="utf-8")
        
    def remove_miner_key(self, key_name: str):
        del self.miner_key_dict[key_name]
        self.miner_keypath.write_text(json.dumps(self.miner_key_dict), encoding="utf-8")
        self.miner_key_dict = json.loads(self.miner_keypath.read_text(encoding="utf-8"))
        
    def update_miner_key(self, key_name: str, miner_config: MinerConfig):
        self.miner_key_dict[key_name] = miner_config
        self.miner_keypath.write_text(json.dumps(self.miner_key_dict), encoding="utf-8")
        self.miner_key_dict = json.loads(self.miner_keypath.read_text(encoding="utf-8"))
    
    def save_miner_keys(self):
        self.miner_keypath.write_text(json.dumps(self.miner_key_dict), encoding="utf-8")

    def load_miner_keys(self):
        self.miner_key_dict = json.loads(self.miner_keypath.read_text(encoding="utf-8"))

    def get_keypair(self, key_name: str):
        json_data = json.loads(Path(f"{self.key_folder_path}/{key_name}.json").read_text(encoding='utf-8'))["data"]
        key_data = json.loads(json_data)
        private_key = key_data["private_key"]
        public_key = key_data["public_key"]
        ss58Key = key_data["ss58_address"]
        return Keypair(private_key, public_key, ss58Key)

    def register_miner(
        self,
        key_name: str,
        external_address: str,
        port: int,
        subnet: str,
        min_stake: int,
        metadata: str
    ):
        address = f"{external_address}:{port}"
        keypair = self.get_keypair(key_name)
        result = comx.register_module(keypair, key_name, address, subnet, min_stake, metadata)
        
        return result.extrinsic
    
    def serve_miner(self, key_name: str, host_address: str, port: int):
        @embedding_router.get(f"/api/v1/process/{key_name}")
        def process(self, request: MinerRequest):
            if request.inference_type == "embedding":
                self.process(request)
                
        self.init_api(
            host_address=host_address,
            port=port,
            router=embedding_router
        )
        
    @abstractmethod
    def process(self, miner_request: MinerRequest) -> Any:
        """Process a request made to the module."""