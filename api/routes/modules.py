import os
import json
from fastapi import APIRouter
from pathlib import Path
from module_registrar.module_registrar import ModuleRegistrar


router = APIRouter()

registrar = ModuleRegistrar()


@router.get("/modules/{module_name}")
def get_module(module_name: str):
    registrar.validate_module(module_name)
    
    