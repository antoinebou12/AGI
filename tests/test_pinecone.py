import pytest
from memory.pinecone import PineconeMemory

@pytest.fixture
def memory_provider():
    return PineconeMemory()

def test_add(memory_provider):
    data = "test data"
    result = memory_provider.add(data)
    assert result.startswith("Inserting data into memory at index:")

def test_get_relevant(memory_provider):
    data = "test data"
    result = memory_provider.get_relevant(data)
    assert isinstance(result, list)

def test_clear(memory_provider):
    result = memory_provider.clear()
    assert result == "Obliviated"

def test_get_stats(memory_provider):
    result = memory_provider.get_stats()
    assert isinstance(result, dict)