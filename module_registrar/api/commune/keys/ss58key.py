from pydantic import BaseModel
from typing import Optional, Any
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