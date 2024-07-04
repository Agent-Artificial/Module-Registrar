import inspect
from fastapi import requests, Request
from fastapi.routing import APIRouter
from fastapi.exceptions import HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from communex._common import get_node_url
from communex.client import CommuneClient

from loguru import logger

rotuer = APIRouter()

comx = CommuneClient(get_node_url())
router = APIRouter()


class QueryParams(BaseModel):
    params: Optional[Dict[str, Any]] = Field(
        None, description="Parameters to pass to the function"
    )


class FunctionArgument(BaseModel):
    name: str
    type: str
    description: str


class FunctionMetadata(BaseModel):
    function: str
    arguments: Dict[str, Any]

    def __init__(self, **kwargs):
        function = kwargs.pop("function")
        arguments = {k: v for k, v in kwargs.items() if k != "function"}
        super().__init__(function=function, arguments=arguments)


@router.get(
    path="/comx/functions",
    summary="List all get_ functions",
    description="Lists all functions from comx that start with 'get_' along with their arguments.",
)
def list_comx_functions():
    """
    Endpoint to list all functions in the CommuneClient that start with 'get_' along with their arguments.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each containing the function name and its arguments that start with 'get_'.
    """
    return [
        FunctionMetadata(
            function=func,
            arguments=[
                FunctionArgument(
                    name=name,
                    type=(
                        str(param.annotation).split("'")[1]
                        if "'" in str(param.annotation)
                        else str(param.annotation)
                    ),
                    description="Argument for the function",
                )
                for name, param in inspect.signature(
                    getattr(comx, func)
                ).parameters.items()
            ],
        )
        for func in dir(comx)
        if callable(getattr(comx, func)) and (func.startswith("get_") or func.startswith("query_map_"))
    ]


@router.get(
    path="/comx/{function_name}",
    summary="Dynamic get_ function caller",
    description="Calls any function from comx that starts with 'get_' with the function name and parameters passed as a parameter.",
)
def get_comx_dynamic(request: Request, function_name: str):
    """
    Dynamic endpoint to call get_ functions in the CommuneClient by function name with additional parameters.

    Args:
        function_name (str): The name of the function to call, which should start with 'get_'.
        params (Optional[Dict[str, Any]]): The parameters to pass to the function, if any.

    Returns:
        Any: The result of the called function.
    """
    params = request.query_params
    try:
        if not function_name.startswith("get_") and not function_name.startswith("query_map_"):
            raise HTTPException(
                status_code=404, detail="Function name must start with 'get_' or 'query_map_."
            )
        func = getattr(comx, function_name)
        if not callable(func):
            raise HTTPException(status_code=404, detail="Function is not callable.")
        sig = inspect.signature(func)
        if params:
            args = tuple(params.values())
            return func(*args)
        else:
            if missing_params := [
                name
                for name, param in sig.parameters.items()
                if param.default is inspect.Parameter.empty
            ]:
                raise HTTPException(
                    status_code=422,
                    detail=f"Missing required arguments: {', '.join(missing_params)}",
                )
            return func()
    except AttributeError as e:
        logger.error(f"Function not found: {str(e)}")
        raise HTTPException(status_code=404, detail="Function not found.") from e
    except TypeError as e:
        logger.error(f"Missing or invalid arguments: {str(e)}")
        raise HTTPException(
            status_code=422, detail=f"Missing or invalid arguments: {str(e)}"
        ) from e
