"""Fetches url data"""

import logging
import urllib.error
import urllib.request

LOGGER = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; rv:27.3) Gecko/20130101 Firefox/27.3"


def fetch_url(url):
    """Fetches the URL using firefox 27 user-agent.

    Input:
        URL

    Output:
        URL content as bytes.

    Raises:
        None
    """
    try:
        headers = {"User-Agent":USER_AGENT}
        page_request = urllib.request.Request(url, headers=headers)
        page_response = urllib.request.urlopen(page_request)
    except ValueError as error:
        LOGGER.debug("Invalid url %s", url)
        return None
    except urllib.error.HTTPError as error:
        LOGGER.debug("Unable to access %s: HTTP error code %d", url, error.code)
        return None
    except urllib.error.URLError as error:
        LOGGER.debug("Unable to read %s: Reason %s", url, error.reason)
        return None
    else:
        return page_response.read()

def fetch_webpage(url):
    """Fetches the webpage at URL.

    Input:
        URL

    Output:
        URL content as utf-8 string.

    Raises:
        None
    """
    data_bytes = fetch_url(url)
    if data_bytes:
        return data_bytes.decode("utf-8")

def fetch_data(url):
    """Fetches the data at URL.

    Input:
        URL

    Output:
        URL content as bytes.

    Raises:
        None
    """
    return fetch_url(url)

def test_main():
    """Tests the current module"""
    link = "http://www.google.com"
    webpage = fetch_webpage(link)
    print(webpage)
    data = fetch_data(link)
    print(data)


if __name__ == "__main__":
    test_main()
