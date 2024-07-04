import uvicorn
import requests
import subprocess
from pydantic import BaseModel
from typing import Dict, List, Union, Optional, Any
from .data_models import Ss58Key, ModuleConfig, MinerConfig, BaseModule
from importlib import import_module
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware


class BaseMiner(BaseModel):
    key_name: str
    key_folder_path: str
    host_address: str
    port: int
    ss58_address: Union[Ss58Key, str]
    use_testnet: bool
    module: BaseModule
    call_timeout: int
    app: FastAPI
    router: APIRouter
    
    def __init__(self, settings: MinerConfig, module_config: ModuleConfig, router: APIRouter):
        self.key_name = settings["key_name"]
        self.key_folder_path = settings["key_folder_path"]
        self.host_address = settings["host_address"]
        self.port = settings["port"]
        self.ss58_address = settings["ss58_address"]
        self.use_testnet = settings["use_testnet"]
        self.call_timeout = settings["call_timeout"]
        self.module = BaseModule(module_config).module
        self.app = FastAPI()
        self.router = router
        super().__init__(**settings)
        
    async def process(self, url: str) -> Any:
        return await self.module.process(url)
    
    def init_api(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.app.add_route("api/v1/process", self)
        
        self.app.add_route("api/v1/modules", self.module)

    def server(self):
        uvicorn.run(self.app, host=self.host_address, port=self.port)
        
        
    