import json
import requests
from generate_llm import generate_gpt


def extract_text_from_link(url):

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    response.encoding = response.encoding or "utf-8"

    prompt = f"""
<persona>
You are a helpful assistant that extracts the raw data from the webpage.
</persona>

<context>
The HTML content of the webpage is {response.text}
</context>

<task>
1. Extract the raw text content from the webpage.
2. Extract the publication date of the document.
3. Extract the title of the document.

The output should be in the following JSON format:
{{
    "title": "The title of the document.",
    "text": "The text from the article of the webpage.
    "publication_date": "The publication date of the document in the
                         format YYYY-MM-DD.",
}}

"""

    llm_parameters = {
        "model": "gpt-5.4-mini",
        "json_mode": True,
    }

    result = json.loads(generate_gpt(prompt, llm_parameters=llm_parameters))
    result["url"] = url
    # print(json.dumps(result, indent=2, ensure_ascii=False))

    return result

