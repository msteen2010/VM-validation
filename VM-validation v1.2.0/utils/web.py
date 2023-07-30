"""
This module provides the web based functions

author: Mike van der Steen
last updated: 31 July 2023
"""

import requests
from utils import log
from requests.adapters import HTTPAdapter, Retry
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
from bs4 import BeautifulSoup

disable_warnings(InsecureRequestWarning)
logger = log.custom_logger()


def title_search(uri: str, text: str) -> bool:
    """
    This function loads a web page and compares the text to title entries on the site
    """

    # Make a call to the URI and pass it to BeautifulSoup for processing
    session = requests.Session()
    retry = Retry(connect=1, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    try:
        page = requests.get(uri, verify=False, timeout=2)
        soup = BeautifulSoup(page.content, 'html.parser')

        # Find all title/s in the HTML content
        child_soup = soup.find_all('title')

        # Search the found entries and compare it against the text provided to the function
        for entry in child_soup:
            if entry.string == text:
                return True
            else:
                return False
    except Exception as e:
        msg = f'Unable to establish connection to {uri} - FQDN not associated with that backup server type'
        logger.info(msg)
        logger.error(str(e))
