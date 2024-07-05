import os
import json
from fastapi import APIRouter
from pathlib import Path
from module_registrar.module_registrar import ModuleRegistrar
from module_registrar.data_models import RegistrarConfig


module_router = APIRouter()


def get_module_registrar(module_name: str):
    registrar_config = RegistrarConfig(
        module_name=module_name,
        target_modules_path=f"module_registrar/modules/{module_name}",
        module_storage_path="modules"
    )
    return ModuleRegistrar(**registrar_config)

@module_router.get("/modules/{module_name}")
def get_module(module_name: str):
    module_registrar = get_module_registrar(module_name)
    if module_name in module_registrar.registry: 
        return module_registrar.registry[module_name]
    else:
        return {"error": f"Module not found.\nAvailable modules: {module_registrar.list_modules()}"}
    
@module_router.get("/modules/public_key")
def get_public_key():
    registrar = get_module_registrar("embedding")
    return {"public_key": registrar.registry["public_key"]}