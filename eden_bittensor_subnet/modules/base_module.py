from typing import Any
from abc import ABC, abstractmethod


class BaseModule:
    @abstractmethod
    async def process(self, url: str) -> Any:
        """Process a request made to the module."""
        


        