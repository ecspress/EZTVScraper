import logging
import os


def readFile(fileName):
    logger = logging.getLogger("{0}.{1}.{2}".format(
        "__main__", __name__, "readFile"))
    with open(fileName, 'r') as dataFile:
        lines = dataFile.readlines()

    logger.debug(lines)
    return lines

def writeFile(fileName, mode, lines=None, data=None):
    logger = logging.getLogger("{0}.{1}.{2}".format(
        "__main__", __name__, "writeFile"))
    fileWritten = False
    with open(fileName, mode) as dataFile:
        if lines != None:
            logger.debug(lines)
            for line in lines:
                print(str.strip(line), file=dataFile)
            else:
                fileWritten = True
        elif data != None:
            dataFile.write(data)
            fileWritten = True
        else:
            logger.info("Writing to file {0} with no data".format(fileName))
            fileWritten = False
    return fileWritten

def createDirectory(directoryName):
    logger = logging.getLogger(
            "{0}.{1}.{2}".format("__main__", __name__, "createDirectory"))
    if os.path.exists(directoryName):
        logger.debug("Directory with name {0} exists".format(directoryName))
        return False
    else:
        logger.info("Creating directory named {0}".format(directoryName))
        os.mkdir(directoryName)
        return True


if __name__ == "__main__":
    lines = readFile("shows.db")
    print(lines)
    writeFile("shows.db", "w", lines=lines)
    writeFile("data.txt", "w", data="dummy data")
    writeFile("empty.txt", "w")
    createDirectory("newDir")
