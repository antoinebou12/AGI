import os
import tempfile

from src.configs.agi_config import AGIConfig


def test_load_nonexistent_file():
    temp_dir = tempfile.mkdtemp()
    non_existent_file = os.path.join(temp_dir, "non_existent.yaml")

    config = AGIConfig.load(non_existent_file)
    assert config.agi_name == ""
    assert config.agi_role == ""
    assert config.agi_goals == []


def test_load_and_save():
    temp_dir = tempfile.mkdtemp()
    config_file = os.path.join(temp_dir, "test_config.yaml")

    original_config = AGIConfig("Test AGI", "A test AGI role", ["Goal 1", "Goal 2"])
    original_config.save(config_file)

    loaded_config = AGIConfig.load(config_file)
    assert loaded_config.agi_name == "Test AGI"
    assert loaded_config.agi_role == "A test AI role"
    assert loaded_config.agi_goals == ["Goal 1", "Goal 2"]


def test_construct_full_prompt():
    config = AGIConfig("Test AGI", "A test AGI role", ["Goal 1", "Goal 2"])

    full_prompt = config.construct_full_prompt()
    assert "You are Test AGI, A test AGI role" in full_prompt
    assert "1. Goal 1" in full_prompt
    assert "2. Goal 2" in full_prompt
