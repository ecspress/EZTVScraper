"""Downloads the latest torrents from eztv"""

import eztv_scraper
import argparse
import data_handler
import datetime
import file_io
import logging
import os
import urllib.parse as urlparse
import web_io

LOGGER = logging.getLogger(__name__)

def get_latest_torrents(shows, download_arguments):
    """Main method of torrentscraper.
    Gets the episodes of each show and calls the relevent fetch method.

    Input:
        list of shows

    Output:
        None

    Raises:
        None
    """
    fetched_count = 0
    show_links = eztv_scraper.parse_showlist_page(eztv_scraper.SHOWLIST_URL)

    if not show_links:
        return

    for show in shows:
        page_link = urlparse.urljoin(eztv_scraper.SITE_URL, show_links[show.name])
        LOGGER.debug("URL for show page -> %s", page_link)
        episodes, unknown_episodes = eztv_scraper.parse_show_page(page_link)

        if not episodes:
            continue

        if unknown_episodes > 0:
            LOGGER.info("Found %d unknown episodes of %s", unknown_episodes, show.name)
        if show.mode == data_handler.MODE_WEEKLY:
            fetched_count += fetch_by_episode(show, episodes, download_arguments)
        else:
            fetched_count += fetch_by_date(show, episodes, download_arguments)
    LOGGER.info("Number of torrents fetched: %d", fetched_count)

def fetch_by_episode(show, episodes, download_arguments):
    """Parses the list of weekly episodes and downloads the latest.

    Input:
        show
        list of episodes of show

    Output:
        None

    Raises:
        None
    """
    fetched_count = 0
    found_new_torrent = False
    for episode in episodes:
        if episode[eztv_scraper.VIDEO_RES_QUALITY] == None:
            comparison_value = compare_episodes(show.season, show.episode,
                                                episode[eztv_scraper.SEASON_NUMBER],
                                                episode[eztv_scraper.EP_NUMBER])
            if comparison_value == -1:
                LOGGER.debug("Skipping previous episodes -> %s",
                             episode[eztv_scraper.TORRENT_TITLE])
                continue
            elif comparison_value == 1:
                LOGGER.info("Found season %d for %s when last episode was -> S%dE%d",
                            episode[eztv_scraper.SEASON_NUMBER], show.name,
                            show.season, show.episode)
                show.season = episode[eztv_scraper.SEASON_NUMBER]

            if download_torrent(show.name, episode, download_arguments):
                LOGGER.info("Downloaded torrent -> %s", episode[eztv_scraper.TORRENT_TITLE])
                fetched_count += 1
                found_new_torrent = True
                show.episode = episode[eztv_scraper.EP_NUMBER]
            else:
                LOGGER.info("Could not download torrent -> %s", episode[eztv_scraper.TORRENT_TITLE])
        else:
            LOGGER.debug("Skipping high def torrents -> %s", episode[eztv_scraper.TORRENT_TITLE])

    if found_new_torrent:
        show.last_updated = datetime.datetime.now().date()
    else:
        LOGGER.info("Found no new episodes for -> %s since %s", show.name, show.last_updated)
    return fetched_count

def fetch_by_date(show, episodes, download_arguments):
    """Parses the list of daily episodes and downloads the latest.

    Input:
        show
        list of episodes of show

    Output:
        None

    Raises:
        None
    """
    fetched_count = 0
    found_new_torrent = False
    for episode in episodes:
        if episode[eztv_scraper.VIDEO_RES_QUALITY] == None:
            episode_date = datetime.date(episode[eztv_scraper.EP_YEAR],
                                         episode[eztv_scraper.EP_MONTH],
                                         episode[eztv_scraper.EP_DATE])
            year, month, day = show.date.split('-')
            last_show_date = datetime.date(int(year), int(month), int(day))
            if last_show_date < episode_date:
                if download_torrent(show.name, episode, download_arguments):
                    LOGGER.info("Downloaded torrent -> %s", episode[eztv_scraper.TORRENT_TITLE])
                    fetched_count += 1
                    found_new_torrent = True
                    show.date = "{0}-{1}-{2}".format(episode[eztv_scraper.EP_YEAR],
                                                     episode[eztv_scraper.EP_MONTH],
                                                     episode[eztv_scraper.EP_DATE])
                else:
                    LOGGER.info("Could not download torrent -> %s",
                                episode[eztv_scraper.TORRENT_TITLE])
            else:
                LOGGER.debug("Skipping previous episodes -> %s",
                             episode[eztv_scraper.TORRENT_TITLE])
        else:
            LOGGER.debug("Skipping high def torrents -> %s", episode[eztv_scraper.TORRENT_TITLE])

    if found_new_torrent:
        show.last_updated = datetime.datetime.now().date()
    else:
        LOGGER.info("Found no new episodes for -> %s since %s", show.name, show.last_updated)
    return fetched_count

def download_torrent(name, episode, download_arguments):
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
    get_torrents, get_magnets, dest_dir = download_arguments

    ep_url = urlparse.urljoin(eztv_scraper.SITE_URL, episode[eztv_scraper.EP_LINK])
    ep_links = eztv_scraper.parse_episode_page(ep_url)

    if not ep_links:
        return False

    if get_torrents:
        torrent_folder = os.path.join(dest_dir, "torrents")
        for link in ep_links[eztv_scraper.TORRENT_FILE_LINK]:
            LOGGER.debug("Downloading torrent -> %s", link)
            data = web_io.fetch_data(link)
            if data and b'<title>Blocked URL</title>' not in data:
                file_path = os.path.join(torrent_folder,
                                         episode[eztv_scraper.TORRENT_TITLE] + ".torrent")
                if file_io.write_file(file_path, 'wb', data=data):
                    downloaded = True
                    break

    if get_magnets:
        folder = os.path.join(dest_dir, "magnets")
        magnet_file = os.path.join(folder, name)
        link = ep_links[eztv_scraper.MAGNET_LINK]
        LOGGER.debug(link)
        downloaded = file_io.write_file(magnet_file, 'a',
                                        [episode[eztv_scraper.TORRENT_TITLE], link])

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

def initialize_logger(dest_dir):
    """Initializes the LOGGER.

    Input:
        None

    Output:
        None

    Raises:
        None
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    log_file = os.path.join(dest_dir, "debug.log")
    file_logger = logging.FileHandler(log_file)
    file_logger.setLevel(logging.DEBUG)
    formatter_for_file = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                                           "%H:%M")
    file_logger.setFormatter(formatter_for_file)

    console_logger = logging.StreamHandler()
    console_logger.setLevel(logging.INFO)
    formatter_for_console = logging.Formatter("%(message)s")
    console_logger.setFormatter(formatter_for_console)

    logger.addHandler(file_logger)
    logger.addHandler(console_logger)

def create_directories(get_torrents, get_magnets, dest_dir):
    """Creates the directories in which torrents and magnets will be stored.

    Input:
        None

    Output:
        None

    Raises:
        None
    """
    if get_torrents:
        folder = os.path.join(dest_dir, "torrents")
        file_io.create_directory(folder)

    if get_magnets:
        folder = os.path.join(dest_dir, "magnets")
        file_io.create_directory(folder)

def main():
    """Starts executing current module"""
    try:
        argument_parser = argparse.ArgumentParser()
        argument_parser.add_argument("dest", help="Specify directory of shows.db")
        argument_parser.add_argument("--magnet", dest="downloadMagnet", action="store_true",
                                     default=False, help="Enables magnet link download")
        argument_parser.add_argument("--torrent", dest="downloadTorrent", action="store_true",
                                     default=False, help="Enables torrent file download")

        arguments = argument_parser.parse_args()
        dest_dir = arguments.dest
        get_torrents = arguments.downloadTorrent
        get_magnets = arguments.downloadMagnet

        download_arguments = (get_torrents, get_magnets, dest_dir)

        initialize_logger(dest_dir)

        if get_torrents or get_magnets:
            create_directories(get_torrents, get_magnets, dest_dir)
            show_file = os.path.join(dest_dir, "shows.db")
            show_data = file_io.read_file(show_file)
            shows = data_handler.convert_text_to_shows(show_data)
            get_latest_torrents(shows, download_arguments)
            show_data = data_handler.convert_shows_to_text(shows)
            file_io.write_file(show_file, "w", show_data)
        else:
            LOGGER.info("Must enable torrent or magnet link option")
    except KeyboardInterrupt:
        print("Exit keyboard combo detected: Exiting....")


if __name__ == "__main__":
    main()
