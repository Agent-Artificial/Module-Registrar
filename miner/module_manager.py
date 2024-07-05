from pydantic import BaseModel
from typing import List
from data_models import ModuleConfig


class ModuleManager(BaseModel):
    modules: List
    
    def get_module(self, module_config: ModuleConfig):
        raise NotImplementedError
    
    def save_module(self):
        raise NotImplementedError