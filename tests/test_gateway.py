import pytest
import sqlite3
from registrar import Registrar


@pytest.fixture
def registrar():
    # Use an in-memory database for testing
    registrar = Registrar(":memory:")
    yield registrar
    registrar.conn.close()


def test_create_tables(registrar):
    cursor = registrar.conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='Validators'"
    )
    assert cursor.fetchone() is not None


def test_get_keypair(registrar):
    public_key, private_key = registrar._get_keypair()
    assert isinstance(public_key, str)
    assert isinstance(private_key, str)
    assert (
        len(private_key) == 64
    )  # Assuming the private key is a 64-character hex string


def test_register(registrar):
    form = {"name": "validator1", "info": "test validator"}
    registrar.register(form)
    cursor = registrar.conn.cursor()
    cursor.execute("SELECT * FROM Validators WHERE id=1")
    validator = cursor.fetchone()
    assert validator is not None
    assert validator[1] is not None  # public_key
    assert validator[2] is not None  # private_key
