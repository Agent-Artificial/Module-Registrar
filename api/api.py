from fastapi import FastAPI, Request, APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import 
from pydantic import BaseModel
from typing import Optional, List, Dict, Union, Any, Tuple
from loguru import logger

from module_registrar.api.commune.data_models import KeyRequest, JINJA2TEMPLATES
from api.commune.routes import router as commune_router
from api.routes.modules import router as module_router


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_route("api/v1/comx", commune_router)
app.add_route("api/v1/modules", module_router)


@app.get("/", response_class=HTMLResponse)
async def get_html(request: Request):
    """
    Retrieves the HTML content of the index page.

    Args:
        request (Request): The incoming request object.

    Returns:
        TemplateResponse: The rendered index.html template with the request object as the context.
    """
    logger.info("Get HTML Request")
    return JINJA2TEMPLATES.TemplateResponse("main.html", {"request": request})