
import json
import requests
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from eden_gateway.gateway import Registrar, RegisterRequest


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CredentialRequest:
    def __init__(self, name, public_key, private_key, ss58_address):
        self.name = name
        self.public_key = public_key
        self.encoded_message = None

@app.get("/credentials")
async def credentials(cred_request: CredentialRequest):
    message = cred_request.encoded_message
    public_key = cred_request.public_key
    name = cred_request.name
    registrar = Registrar()
    registrar.check_register(RegisterRequest(
        sender_public_key=public_key,
        encrypted_message_with_nonce=message,
        message=name
    ))
    return JSONResponse(content="OK")
















    