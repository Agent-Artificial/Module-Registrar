import json
import subprocess
import uvicorn
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, List, Union
from pydantic import BaseModel
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from communex.client import CommuneClient
from communex._common import get_node_url
from module_registrar.base.base_module import BaseModule


comx = CommuneClient(get_node_url())

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MinerRequest(BaseModel):
    data: Optional[Any] = None


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
    miner_config: Optional[Union[MinerConfig, Dict[str, Any]]] = {}
    miner_configs: Optional[Dict[str, Union[MinerConfig, Dict[str, Any]]]] = {}
    miners: Optional[Dict[str, Any]] = {}
    router: Optional[APIRouter] = None
    module: Optional[BaseModule] = None
    
    def __init__(self, miner_config: MinerConfig, module: BaseModule):
        self.miner_config = miner_config
        self.miner_configs = self._load_configs("modules/miner_configs.json")
        self.router = APIRouter()
        self.module = module

    def _load_configs(self, file_path: str) -> List[Dict[str, Any]]:
        path = Path(file_path)
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        configs = []
        path.write_text(json.dumps(configs, indent=4), encoding="utf-8")
        return configs

    def add_route(self, module: BaseModule, app: FastAPI):
        router = APIRouter()
        request_module = module

        @router.get("/modules/{request.module_name}/process")
        async def process_request(request: MinerRequest):
            module_config = {
                "module_name": request.module_name,
                "module_path": request.module_path,
                "module_endpoint": request.module_endpoint,
                "module_url": request.module_url
            }
            module = request_module(**module_config)
            return await module.process(request)

        app.include_router(router)
        
    def _prompt_miner_config(self) -> MinerConfig:
        return MinerConfig(
            miner_name=input("Enter miner_name: "),
            miner_keypath=input("Enter miner_keypath [ex. $HOME/.commune/key/my_miner.json]: ") or None,
            miner_host=input("Enter miner_host [default 0.0.0.0]: ") or "0.0.0.0",
            external_address=input("Enter external_address: ") or None,
            miner_port=int(input("Enter miner_port [default 5757]: ") or 5757),
            stake=float(input("Enter stake [default 275COM]: ") or 275),
            netuid=int(input("Enter netuid [default 0]: ") or 0),
            funding_key=input("Enter funding_key: "),
            funding_modifier=float(input("Enter modifier [default 15COM]: ") or 15),
        )
        
    def serve_miner(self, miner_config: MinerConfig, reload: Optional[bool] = True, register: bool = False):
        if register:
            self.register_miner(miner_config)
        uvicorn.run("base.api:app", host=miner_config.miner_host, port=miner_config.miner_port, reload=reload)
        
    def register_miner(self, miner_config: MinerConfig):
        command = [
            "bash",
            "chains/commune/register_miner.sh",
            "register",
            f"{miner_config.miner_name}",
            f"{miner_config.miner_keypath}",
            f"{miner_config.miner_host}",
            f"{miner_config.port}",
            f"{miner_config.netuid}",
            f"{miner_config.stake}",
            f"{miner_config.funding_key}",
            f"{miner_config.modifier}"
        ]
        subprocess.run(command, check=True)

    @abstractmethod
    def process(self, miner_request: MinerRequest) -> Any:
        self.module.process(miner_request)
