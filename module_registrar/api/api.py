from fastapi import FastAPI, Request, APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Union, Any, Tuple
from loguru import logger

from module_registrar.api.data_models import JINJA2DOCUMENTS, JINJA2TEMPLATES
from module_registrar.api.routes.subnet_routes import commune_router
from module_registrar.api.routes.modules import module_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

app.include_router(module_router)
app.include_router(commune_router)

app.mount("/templates", templates, name="templates")
app.mount("/modules", StaticFiles(directory="modules"), name="modules")


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("module_registrar.api.api:app", host="0.0.0.0", port=8000, reload=True)