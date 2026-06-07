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
    model = llm_parameters.get("model", "gpt-5.5")
    json_mode = llm_parameters.get("json_mode", False)
    temperature = llm_parameters.get("temperature", 0)
    seed = llm_parameters.get("seed", None)
    instructions = llm_parameters.get("instructions", None)

    reasoning_effort = llm_parameters.get("reasoning_effort", "medium")
    verbosity = llm_parameters.get("verbosity", "medium")

    if json_mode:
        text = {"format": {"type": "json_object"}}
    else:
        text = {"format": {"type": "text"}}

    text["verbosity"] = verbosity



    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        input=prompt,
        text=text,
        temperature=temperature,
        )

    return response.output_text


def get_embeddings(texts, model="text-embedding-3-large"):
    response = client.embeddings.create(
        model=model,
        input=texts
    )
    return response.data[0].embedding

