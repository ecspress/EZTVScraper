import EZTVScraper
import argparse
import dataHandler
import datetime
import fileIO
import logging
import os
import sys
import urllib.parse as urlparse
import webIO

destDir = None
getMagnets = None
getTorrents = None
logger = logging.getLogger(__name__)

def get_latest_torrents(shows):
    """Main method of torrentscraper.
    Gets the episodes of each show and calls the relevent fetch method.

    Input:
        list of shows

    Output:
        None

    Raises:
        None
    """
    fetchedCount = 0
    showLinks = EZTVScraper.parse_showlist_page(EZTVScraper.SHOWLIST_URL)
    for show in shows:
        pageLink = urlparse.urljoin(EZTVScraper.SITE_URL, showLinks[show.name])
        logger.debug("URL for show page -> {0}".format(pageLink))
        episodes, unknownEpisodes = EZTVScraper.parse_show_page(pageLink)
        if unknownEpisodes > 0:
            logger.info("Found {0} unknown episodes of {1}".format(
                unknownEpisodes, show.name
            ))
        if show.mode == dataHandler.MODE_WEEKLY:
            fetchedCount += fetch_by_episode(show, episodes)
        else:
            fetchedCount += fetch_by_date(show, episodes)
    logger.info("Number of torrents fetched: {0}".format(fetchedCount))

def fetch_by_episode(show, episodes):
    """Parses the list of weekly episodes and downloads the latest.

    Input:
        show
        list of episodes of show

    Output:
        None

    Raises:
        None
    """
    fetchedCount = 0
    foundNewTorrent = False
    for episode in episodes:
        try:
            if episode[EZTVScraper.VIDEO_RES_QUALITY] == None:
                comparisonValue = compare_episodes(
                            show.season, show.episode,
                            episode[EZTVScraper.SEASON_NUMBER],
                            episode[EZTVScraper.EP_NUMBER]
                        )
                if comparisonValue == -1:
                    logger.debug("Skipping previous episodes -> {0}".format(
                            episode[EZTVScraper.TORRENT_TITLE])
                        )
                    continue
                elif comparisonValue == 1:
                    logger.info(
                            "Found season {0} for {1} when last episode was "\
                            "-> S{2}E{3}".format(
                                episode[EZTVScraper.SEASON_NUMBER], show.name,
                                show.seasonNumber, show.episodeNumber
                            )
                        )
                    show.season = episode[EZTVScraper.SEASON_NUMBER]

                if download_torrent(show.name, episode):
                    logger.info("Downloaded torrent -> {0}".format(
                        episode[EZTVScraper.TORRENT_TITLE]
                    ))
                    fetchedCount += 1
                    foundNewTorrent = True
                    show.episode= episode[EZTVScraper.EP_NUMBER]
                else:
                    logger.info("Could not download torrent -> {0}".format(
                        episode[EZTVScraper.TORRENT_TITLE]
                    ))
            else:
                logger.debug("Skipping high definition torrents -> {0}".format(
                    episode[EZTVScraper.TORRENT_TITLE]
                ))
        except:
            logger.debug("Exception {0} with {1}".format(
                sys.exc_info()[0], episode[EZTVScraper.TORRENT_TITLE]
            ))

    if foundNewTorrent:
        show.lastUpdateTime = datetime.datetime.now().date()
    else:
        logger.info("Found no new episodes for -> {0} since {1}".format(
            show.name, show.lastUpdateTime
        ))
    return fetchedCount

def fetch_by_date(show, episodes):
    """Parses the list of daily episodes and downloads the latest.

    Input:
        show
        list of episodes of show

    Output:
        None

    Raises:
        None
    """
    fetchedCount = 0
    foundNewTorrent = False
    for episode in episodes:
        try:
            if episode[EZTVScraper.VIDEO_RES_QUALITY] == None:
                episodeDate = datetime.date(
                        episode[EZTVScraper.EP_YEAR],
                        episode[EZTVScraper.EP_MONTH],
                        episode[EZTVScraper.EP_DATE])
                lastShowDate = datetime.date(
                        show.year , show.month, show.day)
                if lastShowDate < episodeDate:
                    if download_torrent(show.name, episode):
                        logger.info("Downloaded torrent -> {0}".format(
                            episode[EZTVScraper.TORRENT_TITLE]
                        ))
                        fetchedCount += 1
                        foundNewTorrent = True
                        show.date = episode[EZTVScraper.EP_DATE]
                        show.month = episode[EZTVScraper.EP_MONTH]
                        show.year = episode[EZTVScraper.EP_YEAR]
                    else:
                        logger.info("Could not download torrent -> {0}".format(
                            episode[EZTVScraper.TORRENT_TITLE]
                        ))
                else:
                    logger.debug("Skipping previous episodes -> {0}".format(
                        episode[EZTVScraper.TORRENT_TITLE]
                    ))
            else:
                logger.debug("Skipping high definition torrents -> {0}".format(
                    episode[EZTVScraper.TORRENT_TITLE]
                ))
        except:
            logger.debug("Exception {0} with {1}".format(
                sys.exc_info()[0], episode[EZTVScraper.TORRENT_TITLE]
            ))

    if foundNewTorrent:
        show.lastUpdateTime = datetime.datetime.now().date()
    else:
        logger.info("Found no new episodes for -> {0} since {1}".format(
            show.name, show.lastUpdateTime
        ))
    return fetchedCount 

def download_torrent(name, episode):
    """Downloads the torrent and magnet of episode.

    Input:
        name of show for magnet file name
        dictionary containing details of episodes

    Output:
        None

    Raises:
        None
    """
    downloaded = False

    epUrl = urlparse.urljoin(EZTVScraper.SITE_URL, episode[EZTVScraper.EP_LINK])
    epLinks = EZTVScraper.parse_episode_page(epUrl)

    if getTorrents:
        torrentFolder = os.path.join(rootDir, "torrents")
        links = epLinks[EZTVScraper.TORRENT_FILE_LINK]
        for link in links:
            logger.debug(link)
            data = webIO.fetch_data(link)
            if data and b'<title>Blocked URL</title>' not in data:
                filePath = os.path.join(
                        torrentFolder,
                        episode[EZTVScraper.TORRENT_TITLE] + ".torrent"
                    )
                if fileIO.write_file(filePath, 'wb', data=data):
                    downloaded = True
                    break

    if getMagnets:
        folder = os.path.join(rootDir, "magnets")
        magnetFile = os.path.join(folder, name)
        link = epLinks[EZTVScraper.MAGNET_LINK]
        logger.debug(link)
        downloaded = fileIO.write_file(
                magnetFile, 'a', [episode[EZTVScraper.TORRENT_TITLE], link]
            )

    return downloaded

def compare_episodes(season_1, episode_1, season_2, episode_2):
    """Compares two episodes of a weekly show.

    Input:
        season number of first episode
        episode number of first episode
        season number of second episode
        episode number of second episode

    Output:
        None

    Raises:
        -1 for previous season/episode
        0 for same season new episode
        1 for new season
    """
    if season_1 < season_2:
        return 1
    elif season_1 > season_2:
        return -1
    else:
        if episode_1 < episode_2:
            return 0
        else:
            return -1

def initialize_logger():
    """Initializes the logger.

    Input:
        None

    Output:
        None

    Raises:
        None
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    logFile = os.path.join(rootDir, "debug.log")
    fileLogger = logging.FileHandler(logFile)
    fileLogger.setLevel(logging.DEBUG)
    formatterForFile = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%H:%M")
    fileLogger.setFormatter(formatterForFile)

    consoleLogger = logging.StreamHandler()
    consoleLogger.setLevel(logging.INFO)
    formatterForConsole = logging.Formatter("%(message)s")
    consoleLogger.setFormatter(formatterForConsole)

    logger.addHandler(fileLogger)
    logger.addHandler(consoleLogger)

def create_directories():
    """Creates the directories in which torrents and magnets will be stored.

    Input:
        None

    Output:
        None

    Raises:
        None
    """
    if getTorrents:
        folder = os.path.join(rootDir, "torrents")
        fileIO.create_directory(folder)
        
    if getMagnets:
        folder = os.path.join(rootDir, "magnets")
        fileIO.create_directory(folder)


if __name__ == "__main__":
    argumentParser = argparse.ArgumentParser()
    argumentParser.add_argument("dest", help="Specify directory of shows.db")
    argumentParser.add_argument(
                "--magnet", dest="downloadMagnet", action="store_true",
                default=False, help="Enables magnet link download"
            )
    argumentParser.add_argument(
                "--torrent", dest="downloadTorrent", action="store_true",
                default=False, help="Enables torrent file download"
            )

    arguments = argumentParser.parse_args()
    rootDir = arguments.dest
    getTorrents = arguments.downloadTorrent
    getMagnets = arguments.downloadMagnet

    initialize_logger()

    if getTorrents or getMagnets:
        create_directories()
        showDB = os.path.join(rootDir, "shows.db")
        showData = fileIO.read_file(showDB)
        shows = dataHandler.convert_text_to_shows(showData)
        get_latest_torrents(shows)
        showData = dataHandler.convert_shows_to_text(shows)
        fileIO.write_file(showDB, "w", showData)
    else:
        logger.info("Must enable torrent or magnet link option")
