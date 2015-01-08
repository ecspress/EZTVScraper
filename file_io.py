"""Handles file operations"""

import logging
import os

LOGGER = logging.getLogger(__name__)


def read_file(file_path):
    """Reads lines in a file.

    Input:
        file_path

    Output:
        list of lines in file

    Raises:
        None
    """
    with open(file_path, 'r') as data_file:
        lines = data_file.readlines()

    LOGGER.debug(lines)
    return lines

def write_file(file_path, mode, lines=None, data=None):
    """Reads lines in a file.

    Input:
        file_path

    Output:
        list of lines in file

    Raises:
        None
    """
    file_written = False
    with open(file_path, mode) as data_file:
        if lines:
            LOGGER.debug(lines)
            for line in lines:
                print(str.strip(line), file=data_file)
            file_written = True
        elif data:
            data_file.write(data)
            file_written = True
        else:
            LOGGER.info("Writing to file %s with no data", file_path)
            file_written = False
    return file_written

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
        LOGGER.debug("Directory with name %s exists", directory)
        return False
    else:
        LOGGER.info("Creating directory named %s", directory)
        os.mkdir(directory)
        return True

def test_main():
    """Tests the current module"""
    shows = read_file("sample-shows.db")
    print(shows)
    new_directory = os.path.join('.', "newDir")
    create_directory(new_directory)
    show_file = os.path.join(new_directory, "shows.db")
    write_file(show_file, "w", lines=shows)
    dummy_data_file = os.path.join(new_directory, "data.txt")
    write_file(dummy_data_file, "w", data="dummy data")
    empty_file = os.path.join(new_directory, "empty.txt")
    write_file(empty_file, "w")

if __name__ == "__main__":
    test_main()
