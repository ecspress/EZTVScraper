import EZTVScraper
import argparse
import dataHandler
import datetime
import fileHandler
import logging
import sys
import webIO


def getLatestTorrents(shows, getTorrents, getMagnets, destDir):
    logger = logging.getLogger("{0}.{1}.{2}".format(
        "__main__", __name__, "getLatestTorrents"))
    fetchedCount = 0
    showLinks = EZTVScraper.parseShowlistPage(EZTVScraper.SHOWLIST_URL)
    for show in shows:
        showPageLink = "{0}{1}".format(
                EZTVScraper.SITE_URL, showLinks[show.name])
        logger.debug("URL for show page -> {0}".format(showPageLink))
        showEpisodes = EZTVScraper.parseShowPage(showPageLink)
        if show.showMode == dataHandler.MODE_EPISODAL:
            fetchedCount += fetchByEpisode(
                    show, showEpisodes, getTorrents, getMagnets, destDir)
        else:
            fetchedCount += fetchByDate(
                    show, showEpisodes, getTorrents, getMagnets, destDir)
    logger.info("Number of torrents fetched: {0}".format(fetchedCount))

def fetchByEpisode(show, episodes, getTorrents, getMagnets, destDir):
    logger = logging.getLogger("{0}.{1}.{2}".format(
        "__main__", __name__, "fetchByEpisode"))
    fetchedCount = 0
    foundNewTorrent = False
    for episode in episodes:
        try:
            if episode[EZTVScraper.VIDEO_RES_QUALITY] == None:
                comparisonValue = compareEpisodes(
                        show.seasonNumber, show.episodeNumber,
                        episode[EZTVScraper.SEASON_NUMBER],
                        episode[EZTVScraper.EP_NUMBER])
                if comparisonValue == -1:
                    logger.debug("Skipping previous episodes -> {0}".format(
                        episode[EZTVScraper.TORRENT_TITLE]))
                    continue
                elif comparisonValue == 1:
                    logger.info("Found new season -> {0} for {1} when last "\
                            "episode was -> S{2}E{3}".format(
                                episode[EZTVScraper.SEASON_NUMBER], show.name,
                                show.seasonNumber, show.episodeNumber))
                    show.seasonNumber = episode[EZTVScraper.SEASON_NUMBER]

                if downloadTorrent(
                        show.name, episode, getTorrents, getMagnets, destDir):
                    logger.info("Downloaded torrent for episode -> {0}".format(
                        episode[EZTVScraper.TORRENT_TITLE]))
                    fetchedCount += 1
                    foundNewTorrent = True
                    show.episodeNumber = episode[EZTVScraper.EP_NUMBER]
                else:
                    logger.info("Could not download torrent for -> {0}".format(
                        episode[EZTVScraper.TORRENT_TITLE]))
            else:
                logger.debug("Skipping high definition torrents -> {0}".format(
                    episode[EZTVScraper.TORRENT_TITLE]))
        except:
            logger.debug(
                    "caught Exception {0} with episode title -> {1}".format(
                        sys.exc_info()[0], episode[EZTVScraper.TORRENT_TITLE]))

    if foundNewTorrent:
        show.update = datetime.datetime.now().date()
    else:
        logger.info("Found no new episodes for -> {0} since {1}".format(
            show.name, show.updateTime))
    return fetchedCount

def fetchByDate(show, episodes, getTorrents, getMagnets, destDir):
    logger = logging.getLogger( "{0}.{1}.{2}".format(
        "__main__", __name__, "fetchByDate"))
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
                        show.episodeYear, show.episodeMonth, show.episodeDate)
                if lastShowDate < episodeDate:
                    if downloadTorrent(
                            show.name, episode, getTorrents, getMagnets,
                            destDir):
                        logger.info(
                                "Downloaded torrent for episode -> {0}".format(
                                    episode[EZTVScraper.TORRENT_TITLE]))
                        fetchedCount += 1
                        foundNewTorrent = True
                        show.episodeDate = episode[EZTVScraper.EP_DATE]
                        show.episodeMonth = episode[EZTVScraper.EP_MONTH]
                        show.episodeYear = episode[EZTVScraper.EP_YEAR]
                    else:
                        logger.info(
                                "Could not download torrent for -> {0}".format(
                                    episode[EZTVScraper.TORRENT_TITLE]))
                else:
                    logger.debug("Skipping previous episodes -> {0}".format(
                        episode[EZTVScraper.TORRENT_TITLE]))
            else:
                logger.debug("Skipping high definition torrents -> {0}".format(
                    episode[EZTVScraper.TORRENT_TITLE]))
        except:
            logger.debug(
                    "caught Exception {0} with episode title -> {1}".format(
                        sys.exc_info()[0], episode[EZTVScraper.TORRENT_TITLE]))

    if foundNewTorrent:
        show.updateTime = datetime.datetime.now().date()
    else:
        logger.info("Found no new episodes for -> {0} since {1}".format(
            show.name, show.updateTime))
    return fetchedCount 

def downloadTorrent(name, episode, getTorrents, getMagnets, destDir):
    logger = logging.getLogger("{0}.{1}.{2}".format(
        "__main__", __name__, "downloadTorrent"))
    downloaded = False

    epUrl = "{0}{1}".format( EZTVScraper.SITE_URL, episode[EZTVScraper.EP_LINK])
    epLinks = EZTVScraper.parseEpisodePage(epUrl)

    if getTorrents:
        torrentFolder = "{0}/torrents".format(destDir)
        links = epLinks[EZTVScraper.TORRENT_FILE_LINK]
        for link in links:
            logger.debug(link)
            data = webIO.fetchData(link)
            if data and b'<title>Blocked URL</title>' not in data:
                filePath = "{0}/{1}.torrent".format(
                        torrentFolder, episode[EZTVScraper.TORRENT_TITLE])
                if fileHandler.writeFile(filePath, 'wb', data=data):
                    downloaded = True
                    break

    if getMagnets:
        magnetFile = "{0}/magnets/{1}".format(destDir, name)
        link = epLinks[EZTVScraper.MAGNET_LINK]
        logger.debug(link)
        if fileHandler.writeFile(
                magnetFile, 'a', [episode[EZTVScraper.TORRENT_TITLE], link]):
                downloaded = True

    return downloaded

def compareEpisodes(season_1, episode_1, season_2, episode_2):
    """ returns after comparing _1 with _2 
    -1 for previous season/episode
    0 for same season new episode
    1 for new season"""
    if season_1 < season_2:
        return 1
    elif season_1 > season_2:
        return -1
    else:
        if episode_1 < episode_2:
            return 0
        else:
            return -1

def initializeLogger(currentDirectory):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    fileLogger = logging.FileHandler( "{0}/debug.log".format(currentDirectory))
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

def createDirectories(getTorrents, getMagnets, destDir):
    if getTorrents:
        torrentFolder = "{0}/torrents".format(destDir)
        fileHandler.createDirectory(torrentFolder)
        
    if getMagnets:
        magnetFolder = "{0}/magnets".format(destDir)
        fileHandler.createDirectory(magnetFolder)


if __name__ == "__main__":
    argumentParser = argparse.ArgumentParser()
    argumentParser.add_argument("dest", help="Specify directory of shows.db")
    argumentParser.add_argument(
            "--magnet", dest="downloadMagnet", action="store_true",
            default=False, help="Enables magnet link download")
    argumentParser.add_argument(
            "--torrent", dest="downloadTorrent", action="store_true",
            default=False, help="Enables torrent file download")

    arguments = argumentParser.parse_args()
    rootDir = arguments.dest
    getTorrents = arguments.downloadTorrent
    getMagnets = arguments.downloadMagnet

    initializeLogger(rootDir)

    if getTorrents or getMagnets:
        createDirectories(getTorrents, getMagnets, rootDir)
        showData = fileHandler.readFile("{0}/shows.db".format(rootDir))
        shows = dataHandler.convertTextToShows(showData)
        getLatestTorrents(shows, getTorrents, getMagnets, rootDir)
        showData = dataHandler.convertShowsToText(shows)
        fileHandler.writeFile("{0}/shows.db".format(rootDir), "w", showData)
    else:
        logger = logging.getLogger(__name__)
        logger.info("Must enable torrent or magnet link option")
