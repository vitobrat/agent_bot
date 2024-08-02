from configparser import ConfigParser
import os


def config(filename, section):
    path = os.path.join("config", filename)
    parser = ConfigParser()
    parser.read(path)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f"Section {section} is not found in {filename}")

    return db

