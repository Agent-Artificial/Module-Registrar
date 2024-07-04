from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional, Any, Literal
from substrateinterface.utils import ss58


class Ss58Key(BaseModel):
    ss58_address: str
    
    def __init__(self, address: str) -> None:
        self.address = self.encode(address)
        super().__init__(address=self.address)
    
    def encode(self, public_address: str) -> str:
        encoded_address = ss58.ss58_encode(public_address)
        return self.__setattr__("ss58_address", encoded_address)

    def __str__(self) -> str:
        return str(self.address)
    
    def __setattr__(self, name: str, value: Any) -> None:
        if name == "ss58_address":
            return super().__setattr__(name, value)
        return super().__setattr__(name, self.encode(value))

    def __hash__(self) -> int:
        return hash(self.address)
    

class MinerConfig(BaseModel):
    module_name: Optional[str] = "embedding"
    key_name: Optional[str] = "eden_miner1"
    key_path_name: Optional[str] = "eden_miner1"
    host: Optional[str] = "0.0.0.0"
    port: Optional[int] = 5959


class ModuleConfig(BaseModel):
    def __init__(self, **kwargs):
        super().__setattr__(**kwargs)
        
    def __setattr__(self, name: str, value: Any) -> None:
        if name == "key":
            return super().__setattr__(name, Ss58Key(value))
        return super().__setattr__(name, value)


class BaseModule(BaseModel, ABC):
    def __init__(self, **kwargs) -> None:
        def setattr(self, name: str, value: Any) -> None:
            if name == "key":
                return super().__setattr__(name, Ss58Key(value))
            return super().__setattr__(name, value)
        super().__init__(**kwargs)
        self.__setattr__ = setattr
        
    @abstractmethod
    async def process(self, url: str) -> Any:
        """Process a request made to the module."""


class TokenUsage(BaseModel):
    """Token usage model"""
    total_tokens: int = 0
    prompt_tokens: int = 0
    request_tokens: int = 0
    response_tokens: int = 0
    
class Message(BaseModel):
    content: str
    role: Literal["user", "assistant", "system"]
