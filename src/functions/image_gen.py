import io
import os.path
import uuid
from base64 import b64decode

import openai
import requests
from PIL import Image

from configs import Config


class ImageGenerator:
    def __init__(self, cfg=Config()):
        self.cfg = cfg
        self.working_directory = "auto_gpt_workspace"

    def generate_image(self, prompt):
        filename = f"{str(uuid.uuid4())}.jpg"

        if self.cfg.image_provider == "dalle":
            return self._generate_image_dalle(prompt, filename)
        elif self.cfg.image_provider == "sd":
            return self._generate_image_sd(prompt, filename)
        else:
            return "No Image Provider Set"

    def _generate_image_dalle(self, prompt, filename):
        openai.api_key = self.cfg.openai_api_key

        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="256x256",
            response_format="b64_json",
        )

        print(f"Image Generated for prompt:{prompt}")

        image_data = b64decode(response["data"][0]["b64_json"])

        with open(f"{self.working_directory}/{filename}", mode="wb") as png:
            png.write(image_data)

        return f"Saved to disk:{filename}"

    def _generate_image_sd(self, prompt, filename):
        API_URL = (
            "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4"
        )
        headers = {"Authorization": f"Bearer {self.cfg.huggingface_api_token}"}

        response = requests.post(
            API_URL,
            headers=headers,
            json={
                "inputs": prompt,
            },
        )

        image = Image.open(io.BytesIO(response.content))
        print(f"Image Generated for prompt:{prompt}")

        image.save(os.path.join(self.working_directory, filename))

        return f"Saved to disk:{filename}"
