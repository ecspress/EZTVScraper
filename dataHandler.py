import logging


MODE_DAILY = "Daily"
MODE_EPISODAL = "Episodal"
TIME_UNKNOWN = "Time Unknown"


class Show:
    def __init__(
            self, showName, showMode, seasonNumber=-1, episodeNumber=-1,
            episodeYear=-1, episodeMonth=-1, episodeDate=-1,
            updateTime=TIME_UNKNOWN):
        self.name = showName
        self.showMode = showMode
        self.seasonNumber = int(seasonNumber)
        self.episodeNumber = int(episodeNumber)
        self.updateTime = updateTime
        self.episodeYear = int(episodeYear)
        self.episodeMonth = int(episodeMonth)
        self.episodeDate = int(episodeDate)

def convertTextToShows(lines):
    logger = logging.getLogger(
            "{0}.{1}.{2}".format("__main__", __name__, "convertTextToShows"))
    shows = []
    for line in lines:
        line = line.strip()
        logger.debug(line)
        tokens = line.split('%')
        name = str.strip(tokens[0])
        modeData = str.strip(tokens[1]).split('_')
        time = str.strip(tokens[2])
        if modeData[0] == MODE_DAILY:
            dateTokens = modeData[1].split('-')
            shows.append(
                    Show(name, modeData[0], episodeYear=dateTokens[0],
                        episodeMonth=dateTokens[1], episodeDate=dateTokens[2],
                        updateTime=time))
        elif modeData[0] == MODE_EPISODAL:
            episodeTokens = modeData[1].split(',')
            seasonNumber = episodeTokens[0]
            episodeNumber = episodeTokens[1]
            shows.append(
                    Show(name, modeData[0], seasonNumber=seasonNumber,
                        episodeNumber=episodeNumber, updateTime=time))
        else:
            logger.info("Ignoring show with unknown mode: {0}".format(line))
    return shows

def convertShowsToText(shows):
    logger = logging.getLogger(
            "{0}.{1}.{2}".format("__main__", __name__, "convertShowsToText"))
    lines = []
    for show in shows:
        if show.showMode == MODE_DAILY:
            line = "{0} % {1}_{2}-{3}-{4} % {5}".format(
                    show.name, MODE_DAILY, show.episodeYear, show.episodeMonth,
                    show.episodeDate, show.updateTime)
            lines.append(line)
        else:
            line = "{0} % {1}_{2},{3} % {4}".format(show.name, MODE_EPISODAL,
                    show.seasonNumber, show.episodeNumber,  show.updateTime)
            lines.append(line)
        logger.debug(lines[-1])
    return lines


if __name__ == "__main__":
    lines = [
            "fes % Episodal_12,12 % Time Unknown",
            "fes2 % Daily_2010-01-29 % Time Unknown"
            ]
    print(lines)
    shows = convertTextToShows(lines)
    newLines = convertShowsToText(shows)
    print(newLines)

