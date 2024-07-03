from typing import Any
from abc import ABC, abstractmethod
from pydantic import BaseModel, Generic, Field, PrivateAttr, TypeVar
from type import Dict, Path, Module
from pathlib import Path


T = TypeVar("T")


class ModuleConfig(BaseModel):
    module_name: str
    module_endpoint_url: str
    module_path: Path
    module_paths: Dict[str, Path]
    module_endpoints: Dict[str, str]
    modules: Dict[str, Module]
    key_name: str
    host: str
    port: int


class BaseModule(ABC):
    config: ModuleConfig
    @abstractmethod
    async def process(self, url: str) -> Any:
        """Process a request made to the module."""


