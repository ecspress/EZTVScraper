"""Contains Show class and relevent Methods"""
import logging


MODE_DAILY = "Daily"
MODE_WEEKLY = "Weekly"

LOGGER = logging.getLogger(__name__)


class Show:
    """Object for show information"""
    def __init__(self, showName):
        self.name = showName
        self.mode = None
        self.date = -1
        self.season = -1
        self.episode = -1
        self.last_updated = None

    def set_daily_info(self, date):
        """Sets the date and mode of daily show.

        Input:
            year, month, day

        Output:
            None

        Raises:
            None
        """
        self.mode = MODE_DAILY
        self.date = date

    def set_weekly_info(self, season, episode):
        """Sets the season, episode and mode of weekly show.

        Input:
            season, episode

        Output:
            None

        Raises:
            None
        """
        self.mode = MODE_WEEKLY
        self.season = int(season)
        self.episode = int(episode)

    def set_last_update_time(self, time):
        """Sets the last update time.

        Input:
            time

        Output:
            None

        Raises:
            None
        """
        self.last_updated = time


def convert_text_to_shows(lines):
    """Converts lines in shows.db to Show objects.

    Input:
        list of lines from shows.db

    output:
        list of Show objects

    Raises:
        None

    """
    shows = []
    for line in lines:
        line = line.strip()
        LOGGER.debug(line)
        name, mode_data, time = [token.strip() for token in line.split('%')]
        mode, ep_data = mode_data.split('_')
        show = Show(name)
        show.set_last_update_time(time)
        if mode == MODE_DAILY:
            show.set_daily_info(ep_data)
        elif mode == MODE_WEEKLY:
            season, episode = ep_data.split('-')
            show.set_weekly_info(season, episode)
        else:
            LOGGER.info("Ignoring show with unknown mode: %s", line)
            continue
        shows.append(show)
    return shows

def convert_shows_to_text(shows):
    """Converts list of Show objects to lines for serialization.

    Input:
        list of Shows

    output:
        list of string of serialized Show objects.

    Raises:
        None

    """
    lines = []
    for show in shows:
        if show.mode == MODE_DAILY:
            line = "{0} % {1}_{2} % {3}".format(show.name, MODE_DAILY, show.date,
                                                show.last_updated)
            lines.append(line)
        else:
            line = "{0} % {1}_{2}-{3} % {4}".format(show.name, MODE_WEEKLY, show.season,
                                                    show.episode, show.last_updated)
            lines.append(line)
        LOGGER.debug(lines[-1])
    return lines

def test_main():
    """Tests the current module"""
    lines = ["fes % Weekly_12-12 % Time Unknown", "fes2 % Daily_2010-01-29 % Time Unknown"]
    print(lines)
    shows = convert_text_to_shows(lines)
    print(shows)
    new_lines = convert_shows_to_text(shows)
    print(new_lines)


if __name__ == "__main__":
    test_main()
