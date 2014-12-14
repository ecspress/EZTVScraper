import logging
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; rv:27.3) Gecko/20130101 Firefox/27.3"


def fetch_URL(url):
    """Fetches the URL using firefox 27 user-agent.

    Input:
        URL

    Output:
        URL content as bytes.

    Raises:
        None
    """
    headers = {"User-Agent":USER_AGENT}
    pageRequest = urllib.request.Request(url, headers=headers)
    try:
        pageResponse = urllib.request.urlopen(pageRequest)
    except urllib.error.HTTPError as error:
        logger.error("Unable to reach showlist page with error ", error.code)
        return None
    except urllib.error.URLError as error:
        logger.error("Unable to reach showlist page. Reason: ", error.reason)
        return None
    else:
        return pageResponse.read()

def fetch_webpage(url):
    """Fetches the webpage at URL.

    Input:
        URL

    Output:
        URL content as string.

    Raises:
        None
    """
    data = fetch_URL(url)
    if data:
        return data.decode("utf-8")

def fetch_data(url):
    """Fetches the data at URL.

    Input:
        URL

    Output:
        URL content as bytes.

    Raises:
        None
    """
    return fetch_URL(url)


if __name__ == "__main__":
    url = "http://www.google.com"
    webpage = fetch_webpage(url)
    print(webpage)
    data = fetch_data(url)
    print(data)
