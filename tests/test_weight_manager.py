import pytest
import sqlite3
from weight_manager import WeightManager

@pytest.fixture
def weight_manager():
    # Use an in-memory database for testing
    weight_manager = WeightManager(':memory:')
    yield weight_manager
    weight_manager.conn.close()

def test_create_tables(weight_manager):
    cursor = weight_manager.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Weights'")
    assert cursor.fetchone() is not None

def test_deposit_weights(weight_manager):
    weight_manager.deposit_weights(1, [10, 20, 30])
    cursor = weight_manager.conn.cursor()
    cursor.execute("SELECT * FROM Weights WHERE validator_id=1")
    weights_entry = cursor.fetchone()
    assert weights_entry is not None
    assert weights_entry[1] == '10,20,30'

def test_average_weights(weight_manager):
    weight_manager.deposit_weights(1, [10, 20, 30])
    weight_manager.deposit_weights(2, [20, 30, 40])
    average_weights = weight_manager.average_weights()
    assert average_weights == [15, 25, 35]
