import sqlite3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

app = APIRouter()


class WeightManager:
    def __init__(self, db_path="weights.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        with self.conn:
            self.conn.execute(
                """CREATE TABLE IF NOT EXISTS Weights (
                                    validator_id INTEGER,
                                    weights TEXT,
                                    private_key TEXT,
                                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)"""
            )

    def validate_request(self, public_key: str):
        try:
            self.conn.execute(
                "SELECT private_key FROM Validators WHERE public_key=?", (public_key,)
            )
            #decode something
            return True

    def track_validators(self):
        # Track active validators
        pass

    def deposit_weights(self, validator_id, weights):
        with self.conn:
            self.conn.execute(
                "INSERT INTO Weights (validator_id, weights) VALUES (?, ?)",
                (validator_id, ",".join(map(str, weights))),
            )

    def average_weights(self):
        # Average the weights
        pass

    def transmit_to_blockchain(self):
        # Transmit averaged weights to the blockchain
        pass


weight_manager = WeightManager()


class WeightManagerResponse(BaseModel):
    status: str


class RegisterRequest(BaseModel):
    request_type: str
    validator_id: int
    public_key: str
    weights: list[int]


@app.post("/deposit_weights")
def deposit_weights(deposit_request: RegisterRequest):
    try:
        if validate_request(deposit_request.public_key):

            weight_manager.deposit_weights(
                deposit_request.validator_id, deposit_request.weights
            )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/average_weights")
def average_weights():
    try:
        weight_manager.average_weights()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/transmit_weights")
def transmit_weights():
    try:
        weight_manager.transmit_to_blockchain()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
