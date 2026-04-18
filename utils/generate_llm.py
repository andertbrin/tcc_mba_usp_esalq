import os

from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path



path_project = Path(__file__).parent.parent
secrets_file = os.path.join(path_project, ".env")

load_dotenv(secrets_file)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_gpt(prompt, model="gpt-5.4-mini"):
    response = client.responses.create(
        model=model,
        input=prompt
    )
    return response.output_text


