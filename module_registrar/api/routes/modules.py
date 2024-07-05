import os
import json
from fastapi import APIRouter, Depends
from pathlib import Path
from module_registrar.api.data_models import get_module_registrar


module_router = APIRouter(
    prefix="/modules",
    tags=["items"],
    responses={404: {"description": "Not found"}}
)



@module_router.get("/")
def list_modules():
    registrar = get_module_registrar("embedding")
    return {"modules": registrar.list_modules()}

@module_router.get("/{module_name}")
def get_module(module_name: str):
    module_name = module_name.lower()
    module_registrar = get_module_registrar(module_name)
    if module_name in module_registrar.registry: 
        return module_registrar.registry[module_name]
    else:
        return {"error": f"Module not found.\nAvailable modules: {module_registrar.list_modules()}"}
    
@module_router.get("/public_key")
def get_public_key():
    registrar = get_module_registrar("public_key")
    return {"public_key": registrar.registry["public_key"]}