import logging
import os

logger = logging.getLogger(__name__)


def read_file(filePath):
    """Reads lines in a file.

    Input:
        filePath

    Output:
        list of lines in file

    Raises:
        None
    """
    with open(filePath, 'r') as dataFile:
        lines = dataFile.readlines()

    logger.debug(lines)
    return lines

def write_file(filePath, mode, lines=None, data=None):
    """Reads lines in a file.

    Input:
        filePath

    Output:
        list of lines in file

    Raises:
        None
    """
    fileWritten = False
    with open(filePath, mode) as dataFile:
        if lines:
            logger.debug(lines)
            for line in lines:
                print(str.strip(line), file=dataFile)
            else:
                fileWritten = True
        elif data:
            dataFile.write(data)
            fileWritten = True
        else:
            logger.info("Writing to file {0} with no data".format(filePath))
            fileWritten = False
    return fileWritten

def create_directory(directory):
    """Creates directory.

    Input:
        directory

    Output:
        True if directory created else False

    Raises:
        None
    """
    if os.path.exists(directory):
        logger.debug("Directory with name {0} exists".format(directory))
        return False
    else:
        logger.info("Creating directory named {0}".format(directory))
        os.mkdir(directory)
        return True


if __name__ == "__main__":
    lines = read_file("sample-shows.db")
    print(lines)
    directory= os.path.join('.', "newDir")
    create_directory(directory)
    showFile = os.path.join(directory, "shows.db")
    write_file(showFile, "w", lines=lines)
    dataFile = os.path.join(directory, "data.txt")
    write_file(dataFile, "w", data="dummy data")
    emptyFile = os.path.join(directory, "empty.txt")
    write_file(emptyFile, "w")
