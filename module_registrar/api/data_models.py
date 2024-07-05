import os
from pydantic import BaseModel
from typing import Optional, Union
from fastapi.templating import Jinja2Templates
from module_registrar.api.utilites.local_files import open_local_file

from dotenv import load_dotenv

from communex.compat.key import Ss58Address
from module_registrar.data_models import RegistrarConfig
from module_registrar.module_registrar import ModuleRegistrar

load_dotenv()

JINJA2TEMPLATES = Jinja2Templates(directory="templates")
JINJA2DOCUMENTS = Jinja2Templates(directory="build")

HOST = str(os.getenv("HOST", "0.0.0.0"))
PORT = int(str(os.getenv("PORT", "5959")))


class KeyRequest(BaseModel):
    ss58keys: Optional[Union[str, Ss58Address]]
    

def get_module_registrar(module_name: str):
    return ModuleRegistrar(
        module_name=module_name,
        target_modules_path=f"module_registrar/modules/{module_name}",
        module_storage_path="modules"
    )