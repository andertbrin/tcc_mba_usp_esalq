import json
import requests
import random
import warnings
import os

from generate_llm import generate_gpt
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader


def extract_text_from_link(url, title_pubdate=False):

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    response.encoding = response.encoding or "utf-8"

    if not title_pubdate:
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
    else:
        prompt = f"""
<persona>
You are a helpful assistant that extracts the raw data from the webpage.
</persona>

<context>
The HTML content of the webpage is {response.text}
</context>

<task>
1. Extract the publication date of the document.
2. Extract the title of the document.

The output should be in the following JSON format:
{{
    "title": "The title of the document.",
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


def get_header(headers=False, accept=False, cookie=False):
    """
    Returns a random header for the request.
    https://user-agents.net/browsers/chromium/platforms/linux

    https://www.zenrows.com/blog/web-scraping-headers#user-agent

    """

    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,'
        'like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        ]

    user_agent = random.choice(user_agent_list)

    accepts = {'Accept': '*/*',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
               'User-Agent': 'python-requests/3.31.0',
               'Connection': 'keep-alive'}

    header = {}

    if headers:
        header.update({'User-Agent': user_agent})

    if accept:
        header.update(accepts)

    return header


def extract_pdf_links(url,
                      root=False,
                      only_pdf=True,
                      headers=False,
                      accept=False,
                      verify=True):
    """Extract PDF links from a specific webpage.

    Args:
        url (str): URL of the webpage to extract PDF links from.
        root (str): Root URL of the website for relative link correction.

    Returns:
        list: A list of URLs to PDF files.
    """

    cabecalho = get_header(headers, accept)

    if cabecalho:
        s = requests.Session()
        response = s.get(url, headers=cabecalho, stream=True, verify=verify)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')

    else:
        response = requests.get(url, verify=verify)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')

    # Find all 'a' tags (which define hyperlinks)
    a_tags = soup.find_all('a')

    pdf_links = []
    for tag in a_tags:
        link = tag.get('href')
        text = tag.text
        if link and '.pdf' in link:
            if root and 'http' not in link:
                pdf_links.append(root + link)
            else:
                pdf_links.append(link)
        elif link and not only_pdf:
            if root and 'http' not in link:
                pdf_links.append((root + link, text))
            else:
                pdf_links.append((link, text))

    if not pdf_links:
        warnings.warn('No PDF links found on the page.')

    return pdf_links


# download the pdf file and extract the text from it
def extract_text_from_pdf(url):
    response = requests.get(url)
    response.raise_for_status()

    with open("temp.pdf", "wb") as f:
        f.write(response.content)

    # Extract text from the PDF file
    reader = PdfReader("temp.pdf")
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    # Remove the temporary PDF file
    os.remove("temp.pdf")

    return text
