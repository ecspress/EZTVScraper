from HTMLParserForLinks import HTMLParserForLinks
import logging 
import re 
import urllib.parse
import webIO


logger = logging.getLogger(__name__)

SITE_URL = "https://eztv.it"
#SITE_URL = "https://eztv-proxy.net"
SHOWLIST_URL = "https://eztv.it/showlist/"
#SHOWLIST_URL = "https://eztv-proxy.net/showlist/"

EP_DATE = "episodeDay"
EP_LINK = "episodeLink"
EP_MONTH = "episodeMonth"
EP_NUMBER = "episodeNumber"
EP_YEAR = "episodeYear"
SEASON_NUMBER = "seasonNumber"
TORRENT_TITLE = "torrentTitle"
VIDEO_RES_QUALITY = "resQuality"

MAGNET_LINK = "magnet"
TORRENT_FILE_LINK = "torrent"


def parse_episode_title(title):
    """Parses episode title for information stored in dictionary.

    Input:
        title

    Output:
        episodeInfo as dictionary

    Raises:
        None
    """
    titleInfo = dict()
    title = title.lower()
    matches = re.findall("s\d\de\d\d|\d+x\d+", title)
    if matches:
        episodeID = matches[0].strip('s')
        tokens = []
        if episodeID.find('x') != -1:
            tokens = episodeID.split('x')
        elif episodeID.find('e') != -1:
            tokens = episodeID.split('e')
        else:
            return None
        titleInfo[SEASON_NUMBER] = int(tokens[0])
        titleInfo[EP_NUMBER] = int(tokens[1])
    else:
        matches = re.findall("\d\d\d\d \d\d \d\d", title)
        if matches:
            episodeDate = matches[0].split()
            titleInfo[EP_YEAR] = int(episodeDate[0])
            titleInfo[EP_MONTH] = int(episodeDate[1])
            titleInfo[EP_DATE] = int(episodeDate[2])
        else:
            return None

    matches = re.findall("\d+p|\d+i", title)
    if matches:
        titleInfo[VIDEO_RES_QUALITY] = matches[0]
    else:
        titleInfo[VIDEO_RES_QUALITY] = None

    return titleInfo

def parse_showlist_page(pageUrl):
    """Parses showlist page.

    Input:
        URL of page

    Output:
        showName:ShowURL as dictionary

    Raises:
        None
    """
    pageContent = webIO.fetch_webpage(pageUrl)

    if not pageContent:
        return None

    parser = HTMLParserForLinks()
    parser.parse(pageContent)
    showLinks = dict()
    for link in parser.links:
        if link and link.data and link.attributes:
            if ("class" in link.attributes
                    and link.attributes['class'] == "thread_link"):
                showLinks[link.data] = link.attributes["href"]
    return showLinks

def parse_show_page(pageUrl):
    """Parses showpage.

    Input:
        URL of page

    Output:
        episodes as list
        count of unparsed episodes

    Raises:
        None
    """
    pageContent = webIO.fetch_webpage(pageUrl)

    if not pageContent:
        return None, None

    parser = HTMLParserForLinks()
    parser.parse(pageContent)
    showEpisodes = []
    missedCount = 0
    for link in reversed(parser.links):
        if link and link.data and link.attributes:
            if ("class" in link.attributes
                    and link.attributes['class'] == "epinfo"):
                episodeTitleInfo = parse_episode_title(link.data)
                if episodeTitleInfo:
                    episodeTitleInfo[TORRENT_TITLE] = link.data
                    episodeTitleInfo[EP_LINK] = link.attributes["href"]
                    logger.debug("{0},{1}".format(link.data, episodeTitleInfo))
                    showEpisodes.append(episodeTitleInfo)
                else:
                    missedCount += 1
                    logger.debug(
                            "Can't find episode ID in {0}".format(link.data))
 
    return showEpisodes, missedCount

def parse_episode_page(pageUrl):
    """Parses episode page.

    Input:
        URL of page

    Output:
        dictionary of magnet and torrent links

    Raises:
        None
    """
    pageContent = webIO.fetch_webpage(pageUrl)

    if not pageContent:
        return None

    parser = HTMLParserForLinks()
    parser.parse(pageContent)
    magnetLink = None
    torrentLinks = []
    for link in parser.links:
        if link and link.attributes and "class" in link.attributes:
            if link.attributes['class'].find("magnet") != -1:
                magnetLink = link.attributes["href"]
            elif link.attributes['class'].find("download_") != -1:
                torrentLinks.append(link.attributes["href"])

    return {MAGNET_LINK:magnetLink, TORRENT_FILE_LINK:torrentLinks}


if __name__ == "__main__":
    showLinks = parse_showlist_page(SHOWLIST_URL)
    showCounter = 0
    for show in showLinks.keys():
        showCounter += 1
        showPage = urllib.parse.urljoin(SITE_URL, showLinks[show])
        showEpisodes, unparsedCount = parse_show_page(showPage)
        print(showCounter, show, showLinks[show], showPage, unparsedCount)
        episodeCounter = 0
        for episode in showEpisodes:
            episodeCounter += 1
            epPage = urllib.parse.urljoin(SITE_URL, episode[EP_LINK])
            print(episodeCounter, episode, epPage)
            episodeTorrentLinks = parse_episode_page(epPage)
            print(episodeTorrentLinks)
            if episodeCounter > 2:
                break
        if showCounter > 2:
            break
