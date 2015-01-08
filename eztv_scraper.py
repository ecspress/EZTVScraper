"""Scrapes the EZTV websites"""

from html_link_parser import HTMLLinkParser
import logging
import re
import urllib.parse
import web_io


LOGGER = logging.getLogger(__name__)

SITE_URL = "https://eztv.it"
SHOWLIST_URL = "https://eztv.it/showlist/"
#SITE_URL = "https://eztv-proxy.net"
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
    title_info = dict()
    title = title.lower()
    matches = re.findall(r"s\d\de\d\d|\d+x\d+", title)
    if matches:
        episode_id = matches[0].strip('s')
        tokens = []
        if episode_id.find('x') != -1:
            tokens = episode_id.split('x')
        elif episode_id.find('e') != -1:
            tokens = episode_id.split('e')
        else:
            return None
        title_info[SEASON_NUMBER] = int(tokens[0])
        title_info[EP_NUMBER] = int(tokens[1])
    else:
        matches = re.findall(r"\d\d\d\d \d\d \d\d", title)
        if matches:
            episode_date = matches[0].split()
            title_info[EP_YEAR] = int(episode_date[0])
            title_info[EP_MONTH] = int(episode_date[1])
            title_info[EP_DATE] = int(episode_date[2])
        else:
            return None

    matches = re.findall(r"\d+p|\d+i", title)
    if matches:
        title_info[VIDEO_RES_QUALITY] = matches[0]
    else:
        title_info[VIDEO_RES_QUALITY] = None

    return title_info

def parse_showlist_page(page_url):
    """Parses showlist page.

    Input:
        URL of page

    Output:
        showName:ShowURL as dictionary

    Raises:
        None
    """
    page_content = web_io.fetch_webpage(page_url)

    if not page_content:
        return None

    parser = HTMLLinkParser()
    parser.parse(page_content)
    show_links = dict()
    for link in parser.links:
        if link and link.data and link.attributes:
            if ("class" in link.attributes
                    and link.attributes['class'] == "thread_link"):
                show_links[link.data] = link.attributes["href"]
    return show_links

def parse_show_page(page_url):
    """Parses showpage.

    Input:
        URL of page

    Output:
        episodes as list
        count of unparsed episodes

    Raises:
        None
    """
    page_content = web_io.fetch_webpage(page_url)

    if not page_content:
        return None, None

    parser = HTMLLinkParser()
    parser.parse(page_content)
    show_episodes = []
    missed_count = 0
    for link in reversed(parser.links):
        if link and link.data and link.attributes:
            if ("class" in link.attributes
                    and link.attributes['class'] == "epinfo"):
                title_info = parse_episode_title(link.data)
                if title_info:
                    title_info[TORRENT_TITLE] = link.data
                    title_info[EP_LINK] = link.attributes["href"]
                    LOGGER.debug("%s, %s", link.data, title_info)
                    show_episodes.append(title_info)
                else:
                    missed_count += 1
                    LOGGER.debug("Can't find episode ID in %s", link.data)

    return show_episodes, missed_count

def parse_episode_page(page_url):
    """Parses episode page.

    Input:
        URL of page

    Output:
        dictionary of magnet and torrent links

    Raises:
        None
    """
    page_content = web_io.fetch_webpage(page_url)

    if not page_content:
        return None

    parser = HTMLLinkParser()
    parser.parse(page_content)
    magnet_link = None
    torrent_links = []
    for link in parser.links:
        if link and link.attributes and "class" in link.attributes:
            if link.attributes['class'].find("magnet") != -1:
                magnet_link = link.attributes["href"]
            elif link.attributes['class'].find("download_") != -1:
                torrent_links.append(link.attributes["href"])

    return {MAGNET_LINK:magnet_link, TORRENT_FILE_LINK:torrent_links}

def test_main():
    """Tests the current module"""
    show_links = parse_showlist_page(SHOWLIST_URL)
    show_counter = 0
    for show in show_links.keys():
        show_counter += 1
        show_page = urllib.parse.urljoin(SITE_URL, show_links[show])
        show_episodes, unparsed_count = parse_show_page(show_page)
        print(show_counter, show, show_links[show], show_page, unparsed_count)
        episode_counter = 0
        for episode in show_episodes:
            episode_counter += 1
            ep_page = urllib.parse.urljoin(SITE_URL, episode[EP_LINK])
            print(episode_counter, episode, ep_page)
            episode_torrent_links = parse_episode_page(ep_page)
            print(episode_torrent_links)
            if episode_counter > 2:
                break
        if show_counter > 2:
            break


if __name__ == "__main__":
    test_main()
