import sqlite3
import hashlib
from substrateinterface import Keypair
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from eden_gateway.weight_manager import (
    WeightManager,
    WeightManagerResponse,
    deposit_weights,
    average_weights,
    transmit_weights,
)
from eden_gateway.weight_manager import app as weight_router
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_api_route(
    path="deposit_weights",
    methods=["POST"],
    name="deposit_weights",
    include_in_schema=False,
    endpoint=deposit_weights(),
)

app.add_route(
    route=weight_router,
    path="average_weights",
    methods=["POST"],
    name="average_weights",
    include_in_schema=False,
)
app.add_route(
    route=transmit_weights,
    path="transmit_weights",
    methods=["POST"],
    name="transmit_weights",
    include_in_schema=False,
)


class Registrar:
    def __init__(self, db_path="registry.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        with self.conn:
            self.conn.execute(
                """CREATE TABLE IF NOT EXISTS Validators (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    public_key TEXT,
                                    private_key TEXT,
                                    whitelisted BOOLEAN)"""
            )

    def _open_registry(self):
        # Encrypt and open the registry database
        pass

    def register(self, form):
        # Validate form and check whitelist
        # Generate keypair and store in the database
        pass

    def _get_keypair(self):
        keypair = Keypair.create_from_mnemonic(Keypair.generate_mnemonic())
        public_key = keypair.ss58_address
        private_key = keypair.seed_hex
        return public_key, private_key

    def _encode_message(self, message, public_key):
        # Encode the message with the public key
        pass

    def _check_registry(self, validator_id):
        # Query the registry for validator information
        pass


registrar = Registrar()


@app.post("/register")
def register_validator(form: dict):
    try:
        registrar.register(form)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
