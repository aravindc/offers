from configparser import ConfigParser
import logging
import os.path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_mysql_config(filename='config.ini', section='mysql'):
    parser = ConfigParser()
    parser.read([os.path.dirname(__file__).replace('\\', '/')+'/'+filename])
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section,
                        filename))
    return db


def read_pg_config(filename='config.ini', section='pgsql'):
    #  create a parser
    parser = ConfigParser()
    #  read config file
    parser.read(os.path.dirname(__file__).replace('\\', '/')+'/'+filename)
    #  get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section,
                        filename))
    return db
