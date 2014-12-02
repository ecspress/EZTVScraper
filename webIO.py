import logging
import urllib.error
import urllib.request


USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; rv:27.3) Gecko/20130101 Firefox/27.3"


def fetchURL(url):
    logger = logging.getLogger(
            "{0}.{1}.{2}".format("__main__", __name__, "fetchWebpage"))
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

def fetchWebpage(url):
    return fetchURL(url).decode("utf-8")

def fetchData(url):
    return fetchURL(url)


if __name__ == "__main__":
    url = "http://www.google.com"
    webpage = fetchWebpage(url)
    print(webpage)
    data = fetchData(url)
    print(data)
