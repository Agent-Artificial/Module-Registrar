from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class MinerRequest(BaseModel):
    data: Optional[List[str]]
    model: Optional[str]
    config: Optional[Dict[str, Any]]