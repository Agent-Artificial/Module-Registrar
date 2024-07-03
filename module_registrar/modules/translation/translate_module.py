import argparse
import requests

from overrides import override
from module_registrar.modules.base_module import BaseModule
from module_registrar.modules.translation.data_models import TranslationRequest
from typing import Any


class TranslateMiner(BaseModule):

    def __init__(self, get_config):
        super().__init__()
        self.config = get_config()

    @override
    def process(self, url: str, request: MinerRequest) -> Any:
        """Process a request made to the module."""
        
        



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