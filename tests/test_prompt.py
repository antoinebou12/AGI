import pytest
from pathlib import Path
from src.prompt import load_prompt

def test_load_prompt_success(tmpdir):
    # Create a temporary file with sample content
    prompt_file_path = tmpdir / "data" / "prompt.txt"
    prompt_file_path.parent.mkdir()
    prompt_content = "This is a test prompt."
    with open(prompt_file_path, "w") as prompt_file:
        prompt_file.write(prompt_content)

    # Temporarily change the __file__ attribute to the tmpdir
    original_file = your_module.__file__
    your_module.__file__ = str(tmpdir / "your_module.py")

    # Test the function
    assert load_prompt() == prompt_content

    # Restore the original __file__ attribute
    your_module.__file__ = original_file

def test_load_prompt_failure(tmpdir):
    # Temporarily change the __file__ attribute to the tmpdir
    original_file = your_module.__file__
    your_module.__file__ = str(tmpdir / "your_module.py")

    # Test the function
    with pytest.raises(FileNotFoundError):
        load_prompt()

    # Restore the original __file__ attribute
    your_module.__file__ = original_file