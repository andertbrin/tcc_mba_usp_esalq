import os

from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
from typing import Dict

path_project = Path(__file__).parent.parent
secrets_file = os.path.join(path_project, ".env")

load_dotenv(secrets_file)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_gpt(prompt, llm_parameters: Dict):
    model = llm_parameters.get("model", "gpt-5.4-mini")
    json_mode = llm_parameters.get("json_mode", False)

    request_args = {
        "model": model,
        "input": prompt,
    }

    if json_mode:
        request_args["text"] = {"format": {"type": "json_object"}}
    else:
        request_args["text"] = {"format": {"type": "text"}}

    response = client.responses.create(**request_args)
    return response.output_text


