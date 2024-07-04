from typing import Any, Dict
from abc import ABC, abstractmethod
from pydantic import BaseModel
from pathlib import Path


class ModuleConfig(BaseModel):
    module_name: str
    module_endpoint_url: str
    module_path: Path
    module_paths: Dict[str, Path]
    module_endpoints: Dict[str, str]
    modules: Dict[str, Dict[str, Any]]
    key_name: str
    host: str
    port: int


class BaseModule(ABC):
    config: ModuleConfig
    @abstractmethod
    async def process(self, url: str) -> Any:
        """Process a request made to the module."""


