import json
import os

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import requests
from bs4 import BeautifulSoup


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


def get_statements_minutes_links():
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

