from HTMLParserForLinks import HTMLParserForLinks
import logging 
import re 
import webIO


SITE_URL = "https://eztv.it"
SHOWLIST_URL = "https://eztv.it/showlist/"


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


def parseEpisodeTitle(titleData):
    logger = logging.getLogger(
            "{0}.{1}.{2}".format("__main__", __name__, "parseEpisodeTitle"))
    titleInfo = dict()
    titleData = titleData.lower()
    matches = re.findall("s\d\de\d\d|\d+x\d+", titleData)
    if len(matches) > 0:
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
        matches = re.findall("\d\d\d\d \d\d \d\d", titleData)
        if len(matches) > 0:
            episodeDate = matches[0].split()
            titleInfo[EP_YEAR] = int(episodeDate[0])
            titleInfo[EP_MONTH] = int(episodeDate[1])
            titleInfo[EP_DATE] = int(episodeDate[2])
        else:
            return None

    matches = re.findall("\d+p|\d+i", titleData)
    if len(matches) > 0:
        quality = matches[0]
        titleInfo[VIDEO_RES_QUALITY] = quality
    else:
        titleInfo[VIDEO_RES_QUALITY] = None

    logger.debug("{0},{1}".format(titleData, titleInfo))
    return titleInfo

def parseShowlistPage(pageUrl):
    logger = logging.getLogger(
            "{0}.{1}.{2}".format("__main__", __name__, "parseShowlistPage"))
    pageContent = webIO.fetchWebpage(pageUrl)
    parser = HTMLParserForLinks()
    parser.parse(pageContent)
    showLinks = dict()
    for link in parser.links:
        if link and link.data and link.attributes:
            if ("class" in link.attributes
                    and link.attributes['class'] == "thread_link"):
                showLinks[link.data] = link.attributes["href"]
    return showLinks

def parseShowPage(pageUrl):
    logger = logging.getLogger(
            "{0}.{1}.{2}".format("__main__", __name__, "parseShowPage"))
    pageContent = webIO.fetchWebpage(pageUrl)
    parser = HTMLParserForLinks()
    parser.parse(pageContent)
    showEpisodes = []
    for link in reversed(parser.links):
        if link and link.data and link.attributes:
            if ("class" in link.attributes
                    and link.attributes['class'] == "epinfo"):
                episodeTitleInfo = parseEpisodeTitle(link.data)
                if episodeTitleInfo == None:
                    logger.debug(
                            "Can't find episode ID in {0}".format(link.data))
                else:
                    episodeTitleInfo[TORRENT_TITLE] = link.data
                    episodeTitleInfo[EP_LINK] = link.attributes["href"]
                    showEpisodes.append(episodeTitleInfo)
                    
    return showEpisodes

def parseEpisodePage(pageUrl):
    logger = logging.getLogger(
            "{0}.{1}.{2}".format("__main__", __name__, "parseEpisodePage"))
    pageContent = webIO.fetchWebpage(pageUrl)
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
    showLinks = parseShowlistPage(SHOWLIST_URL)
    showCounter = 0
    for show in showLinks.keys():
        showCounter += 1
        print(showCounter, show, showLinks[show])
        showEpisodes = parseShowPage("{0}{1}".format(SITE_URL, showLinks[show]))
        episodeCounter = 0
        for episode in showEpisodes:
            episodeCounter += 1
            print(episodeCounter, episode)
            episodeTorrentLinks = parseEpisodePage(
                    "{0}{1}".format(SITE_URL,episode[EP_LINK]))
            print(episodeTorrentLinks)
            if episodeCounter > 3:
                break
        if showCounter > 3:
            break
