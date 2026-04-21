import json
import os
import re
import requests

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from urllib.parse import urljoin

from bs4 import BeautifulSoup


SPEECH_SELECTOR = 'a[href*="/newsevents/speech/"]'
TESTIMONY_SELECTOR = 'a[href*="/newsevents/testimony/"]'
NEXT_BUTTON_XPATH = (
    "//a[normalize-space()='Next' or contains(@aria-label, 'Next') or contains(@title, 'Next')]"
    " | "
    "//button[normalize-space()='Next' or contains(@aria-label, 'Next') or contains(@title, 'Next')]"
)

ENTRY_HREF_PATTERN = re.compile(
    r"/newsevents/(?P<kind>speech|testimony)/[a-z]+(?P<date>\d{8})(?P<suffix>[a-z])\.htm$",
    re.IGNORECASE,
)



def extract_index_fomc_materials(path_data):
    '''
    Extrai um índice de todos os links dos materiais que o FED disponibiliza em
    'https://www.federalreserve.gov/monetarypolicy/materials/'

    Args:
        url: 'https://www.federalreserve.gov/monetarypolicy/materials/'
        (ou a mais atual)

    Return:
        links: lista com os links.
    '''
    # Set up a web driver
    url = 'https://www.federalreserve.gov/monetarypolicy/materials/'
    driver = webdriver.Edge()
    driver.get(url)
    # Find all the element nodes in the body excluding
    # script and style elements
    last_update = WebDriverWait(driver, 35).until(
        EC.presence_of_element_located((By.CLASS_NAME, "lastUpdate"))).text
    last_update = last_update.split(':')[-1].lstrip()

    link_list = list()

    x = 0
    while x < 100:
        x += 1
        (WebDriverWait(driver, 35).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Next'))))
        elements = driver.find_elements(By.LINK_TEXT, 'HTML')
        for item in elements:
            link_list.append(item.get_property('href'))
        next_page = driver.find_elements(By.LINK_TEXT, 'Next')[0]

        driver.execute_script("window.scrollTo(0, 300)")
        disabled = driver.find_elements(By.CLASS_NAME, 'disabled')
        if len(disabled) > 0 and (disabled[0].text == 'Next'):
            break
        next_page.click()

    with open(os.path.join(path_data, 'links_list.json'), 'w') as f:
        json.dump(link_list, f, indent=2)


def get_fomc_links():
    """
    retorna uma tupla com duas listas: uma com os links para
    os statements e outra com os links para as minutas
    """

    root = 'https://www.federalreserve.gov'
    url = 'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm'

    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    a_tags = soup.find_all('a')

    links = []
    for tag in a_tags:
        link = tag.get('href')
        if link and link.endswith('.htm') and 'minutes' in link:
            if root and 'http' not in link:
                links.append(root + link)

        if link and link.endswith('.htm') and 'pressreleases/monetary' in link:
            if root and 'http' not in link:
                links.append(root+link)

        if link and link.endswith('.htm') and 'fomcpresscon' in link:
            if root and 'http' not in link:
                links.append(root+link)

        if link and link.endswith('.htm') and 'fomcprojtabl' in link:
            if root and 'http' not in link:
                links.append(root+link)

    return links


# links dos discursos e testemunhos dos membros do FED

def _entry_anchors(driver):
    anchors = driver.find_elements(
        By.CSS_SELECTOR,
        f"{SPEECH_SELECTOR}, {TESTIMONY_SELECTOR}",
    )
    valid_anchors = []

    for anchor in anchors:
        href = anchor.get_attribute("href")
        title = anchor.text.strip()

        if not href or not title:
            continue

        if not ENTRY_HREF_PATTERN.search(href):
            continue

        valid_anchors.append(anchor)

    return valid_anchors


def _wait_for_results_page(wait, min_results=10):
    wait.until(lambda d: len(_entry_anchors(d)) >= min_results)


def _get_page_marker(driver):
    anchors = _entry_anchors(driver)
    if anchors:
        return anchors[0].get_attribute("href")
    return None


def _extract_entries_from_current_page(driver, seen, page_number, base_url):
    page_entries = []

    for anchor in _entry_anchors(driver):
        href = anchor.get_attribute("href")
        title = anchor.text.strip()

        match = ENTRY_HREF_PATTERN.search(href)
        if not match or href in seen:
            continue

        seen.add(href)

        page_entries.append(
            {
                "title": title,
                "url": urljoin(base_url, href),
                "date": match.group("date"),
                "type": match.group("kind"),
                "page": page_number,
            }
        )

    return page_entries


def _go_to_next_page(driver, wait, previous_marker):
    next_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, NEXT_BUTTON_XPATH))
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        next_button,
    )
    driver.execute_script("arguments[0].click();", next_button)

    wait.until(
        lambda d: (_get_page_marker(d) is not None)
        and (_get_page_marker(d) != previous_marker)
    )

    _wait_for_results_page(wait)


def extract_speeches_testimony_links(
    url="https://www.federalreserve.gov/newsevents/speeches-testimony.htm",
    next_pages=100,
):
    driver = webdriver.Edge()
    wait = WebDriverWait(driver, 35)

    try:
        driver.get(url)

        last_update = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "lastUpdate"))
        ).text
        last_update = last_update.split(":", 1)[-1].strip()

        _wait_for_results_page(wait)

        cutoff_date = "20150101"
        seen = set()
        all_entries = []
        total_pages = next_pages + 1

        for page_number in range(1, total_pages + 1):
            page_entries = _extract_entries_from_current_page(
                driver, seen, page_number, url
            )

            stop = False
            for entry in page_entries:
                if entry["date"] < cutoff_date:
                    stop = True
                else:
                    all_entries.append(entry)

            if stop or page_number == total_pages:
                break

            previous_marker = _get_page_marker(driver)

            try:
                _go_to_next_page(driver, wait, previous_marker)
            except TimeoutException:
                break

        return {
            "last_update": last_update,
            "count": len(all_entries),
            "pages_scraped": page_number,
            "links": all_entries,
        }

    finally:
        driver.quit()
