from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class MinerRequest(BaseModel):
    data: Optional[Dict[str, Any]]
    model: Optional[str]
    config: Optional[Dict[str, Any]]


class RegistrarConfig(BaseModel):
    module_name: str
    target_modules_path: str
    module_storage_path: str