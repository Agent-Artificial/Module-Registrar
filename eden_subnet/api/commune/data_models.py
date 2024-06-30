import os
from pydantic import BaseModel
from typing import Optional, Union
from fastapi.templating import Jinja2Templates

from communex.compat.key import Ss58Address


JINJA2TEMPLATES = Jinja2Templates(directory="templates")
JINJA2DOCUMENTS = Jinja2Templates(directory="build")

HOST = str(os.getenv("HOST", "0.0.0.0"))
PORT = int(str(os.getenv("PORT", "5959")))


class KeyRequest(BaseModel):
    ss58keys: Optional[Union[str, Ss58Address]]
    
