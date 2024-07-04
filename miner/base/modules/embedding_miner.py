from miner.base_miner import BaseMiner, BaseModule, ModuleConfig, MinerConfig, MinerRequest


embedding_miner_config = MinerConfig(
    key_name="embedding_miner_1",
    key_folder_path="$HOME/.commune/key",
    host_address="0.0.0.0",
    port=5959,
    ss58_address="5HmGKcFPJe8Loxc59icLv2Znxwfx7nyUiyDGrwz6fhNbVr5u",
    use_testnet=True,
    call_timeout=10
)

embedding_module_config = ModuleConfig(
    module_name="embedding",
    module_path="modules/embedding",
    module_endpoint="https://raw.githubusercontent.com/commune-network/commune/main/modules/embedding/embedding.py",
)
class EmbeddingMiner(BaseMiner):
    