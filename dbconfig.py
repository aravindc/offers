from configparser import ConfigParser
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_db_config(filename='/opt/offers/config.ini', section='mysql'):
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))
    return db

