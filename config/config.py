"""
This module provide to get secret data from config.ini file

Example of config.ini:

    [postgresql]
    host = ***
    database = ***
    user = ***
    port = ***
    password = ***

    [tokens]
    bot_token = ***
    api_token = ***

    [urls]
    articles_url = https://ru.investing.com/news/cryptocurrency-news
"""
from configparser import ConfigParser
import os


def config(filename, section):
    """Parse data from config.ini with secret data"""
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

