import os
import json
from pydantic import BaseModel
from typing import List, Dict, Any
from data_models import ModuleConfig
from base.base_module import BaseModule
from importlib import import_module


class ModuleManager(BaseModel):
    module_configs = List[ModuleConfig]
    modules: Dict[str, Any]
    
    def __init__(self):
        self.modules = {}
        self.active_modules = {}
        self.module_configs = self.get_configs()
        
    def get_configs(self):
        configs = []
        if os.path.exists("data/instance_data/module_configs.json"):
            with open("data/instance_data/module_configs.json", "r", encoding="utf-8") as f:
                configs = json.loads(f.read())
        else:
            with open("data/instance_data/module_configs.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(configs, indent=4))
        return configs

    def get_module(self):
        for config in self.module_configs:
            module_name = config.module_name
            for dir in os.listdir("modules"):
                if config in dir:
                    module = import_module(f"{dir}.{module_name}")
                    self.modules[module_name] = module
        with open("modules/registry.json", "w", encoding="utf-8") as f:
            f.write(self.modules)
        return self.modules
    
    def install_module(self, module: BaseModule, module_config: ModuleConfig):
        module = module()
        module.install_module(module_config)
        self.active_modules[module_config.module_name] = module
        return module
    
    def remove_module(self, module_config: ModuleConfig):
        if module_config.module_name in self.active_modules:
            del self.active_modules[module_config.module_name]
        return self.active_modules
    
    def get_active_modules(self):
        return self.active_modules
    
    def save_module(self, module_config: ModuleConfig, module_data):
        module = self.active_modules[module_config.module_name]
        module.save_module(module_config, module_data)
        
    def register_module(self, module_config: ModuleConfig):
        command = f"bash modules"
        

        
        

def cli():
    manager = ModuleManager()
    manager.get_configs()
    manager.get_active_modules()
    print("Module manager CLI")
    options = {
        "1": ("Add a Module Config", lambda: manager.add_module_config()),
        "1": ("Add Module", lambda: .add_module(module_name, f"module_registrar/modules/{module_name}")),
        "2": ("Update Module", lambda: registrar.update_module(module_name, f"module_registrar/modules/{module_name}")),
        "3": ("Remove Module", lambda: registrar.remove_module(module_name)),
        "4": ("List Modules", lambda: print("Modules: ", registrar.list_modules())),
        "5": ("Exit", lambda: exit(0))
    }

    while True:
        print("\nModule Registry:", registrar.registry)
        print("\nOptions:")
        for key, (description, _) in options.items():
            print(f"{key}. {description}")

        choice = input("Enter your choice: ")
        if choice in options:
            options[choice][1]()
        else:
            print("Invalid choice. Please try again.")