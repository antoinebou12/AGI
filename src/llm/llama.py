# subprocess with llama

import os
import subprocess
import sys
import time
import threading
import itertools
import time

from rich.spinner import Spinner as RichSpinner
from rich.console import Console

# download llama
# # build this repo
# git clone https://github.com/ggerganov/llama.cpp
# cd llama.cpp
# make

# #For Windows and CMake, use the following command instead:
# cd <path_to_llama_folder>
# mkdir build
# cd build
# cmake ..
# cmake --build . --config Release

# # obtain the original LLaMA model weights and place them in ./models
# ls ./models
# 65B 30B 13B 7B tokenizer_checklist.chk tokenizer.model

# # install Python dependencies
# python3 -m pip install torch numpy sentencepiece

# # convert the 7B model to ggml FP16 format
# python3 convert-pth-to-ggml.py models/7B/ 1

# # quantize the model to 4-bits (using method 2 = q4_0)
# ./quantize ./models/7B/ggml-model-f16.bin ./models/7B/ggml-model-q4_0.bin 2

# # run the inference
# ./main -m ./models/7B/ggml-model-q4_0.bin -n 128

def download_llama():
    console = Console()

    with console.status("[bold green]Downloading Llama...") as status:
        subprocess.run(["git", "clone", "https://github.com/ggerganov/llama.cpp"])
        time.sleep(2)

def build_llama():
    console = Console()

    with console.status("[bold green]Building Llama...") as status:
        subprocess.run(["cd", "llama.cpp"])
        subprocess.run(["mkdir", "build"])
        subprocess.run(["cd", "build"])
        subprocess.run(["cmake", ".."])
        subprocess.run(["cmake", "--build", ".", "--config", "Release"])
        time.sleep(2)

def download_model():
    console = Console()

    with console.status("[bold green]Downloading Llama model...") as status:
        subprocess.run(["ls", "./models"])
        subprocess.run(["65B", "30B", "13B", "7B", "tokenizer_checklist.chk", "tokenizer.model"])
        time.sleep(2)

def convert_model():
    console = Console()

    with console.status("[bold green]Converting Llama model...") as status:
        subprocess.run(["python3", "convert-pth-to-ggml.py", "models/7B/", "1"])
        time.sleep(2)

def quantize_model():
    console = Console()

    with console.status("[bold green]Quantizing Llama model...") as status:
        subprocess.run(["./quantize", "./models/7B/ggml-model-f16.bin", "./models/7B/ggml-model-q4_0.bin", "2"])
        time.sleep(2)

def run_inference():
    console = Console()

    with console.status("[bold green]Running Llama inference...") as status:
        subprocess.run(["./main", "-m", "./models/7B/ggml-model-q4_0.bin", "-n", "128"])
        time.sleep(2)

def main():
    download_llama()
    build_llama()
    download_model()
    convert_model()
    quantize_model()
    run_inference()