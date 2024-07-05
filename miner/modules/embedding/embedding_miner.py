import os
from miner.base_miner import BaseMiner, BaseModule, ModuleConfig, MinerConfig, MinerRequest
from dotenv import load_dotenv
from pathlib import Path
from fastapi import FastAPI, APIRouter
from communex.client import CommuneClient
from communex._common import get_node_url

comx = CommuneClient(get_node_url())

embedding_router = APIRouter()

load_dotenv()

embedding_module_config = ModuleConfig(
    module_name="translation",
    module_path="modules/translation",
    module_url=f"http://localhost:8000/modules",
    module_endpoint="/modules/translation"
)

embedding_module = BaseModule(embedding_module_config)


def get_miner_config():
    return MinerConfig(
        key_name=input("key_name: ") or "embedding_miner_1",
        key_folder_path="$HOME/.commune/key",
        host_address=input("host_address: ") or "0.0.0.0",
        external_address=input("external_address: ") or "0.0.0.0",
        port=input("port: ") or 8000,
        ss58_address="",
        use_testnet=input("use_testnet(True/False): ") or False,
        module=embedding_module,
        call_timeout=input("call_timeout: ") or 30,
        app=FastAPI(),
        router=APIRouter()
    )


class EmbeddingMiner(BaseMiner):
    def __init__(self, settings: MinerConfig, config: ModuleConfig, router: APIRouter):
        super().__init__(
            settings=settings,
            config=config,
            router=router
        )
        self.
        self.init_module(settings)
        
    def process(self, miner_request: MinerRequest):
        return self.tokenizer(miner_request.data)
        
if __name__ == "__main__":
    miner_config = get_miner_config()
    embedding_miner = EmbeddingMiner(miner_config, embedding_module_config, embedding_router)
    embedding_miner.init_api(miner_config.host_address, miner_config.port, embedding_router)
    embedding_miner.server(miner_config.host_address, miner_config.port)
    