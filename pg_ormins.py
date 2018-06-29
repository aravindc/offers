from datetime import datetime, timedelta
import uuid
from pony import orm
import json
import logging
from dbconfig import read_pg_config
import argparse
import os
import sys


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

params = read_pg_config()

db = orm.Database()
db.bind(provider='postgres', user=params['user'], password=params['password'],
        host=params['host'], database=params['database'])


class Morrison(db.Entity):
    id = orm.PrimaryKey(uuid.UUID, default=uuid.uuid4, auto=True)
    data = orm.Required(orm.Json)
    ins_ts = orm.Required(datetime)


class Ocado(db.Entity):
    id = orm.PrimaryKey(uuid.UUID, default=uuid.uuid4, auto=True)
    data = orm.Required(orm.Json)
    ins_ts = orm.Required(datetime)


class Sainsburys(db.Entity):
    id = orm.PrimaryKey(uuid.UUID, default=uuid.uuid4, auto=True)
    data = orm.Required(orm.Json)
    ins_ts = orm.Required(datetime)


class Tesco(db.Entity):
    id = orm.PrimaryKey(uuid.UUID, default=uuid.uuid4, auto=True)
    data = orm.Required(orm.Json)
    ins_ts = orm.Required(datetime)


class Asda(db.Entity):
    id = orm.PrimaryKey(uuid.UUID, default=uuid.uuid4, auto=True)
    data = orm.Required(orm.Json)
    ins_ts = orm.Required(datetime)


# orm.sql_debug(True)
db.generate_mapping(create_tables=True)


def ins_all_files(retailer):
    files = [f for f in os.listdir('./'+retailer+'_*.json') if os.path.isfile(f)]
    for f in files:
        logger.info(f)


@orm.db_session
def ins_data(insFile, insDt, retailer):
    with open(insFile, 'r+', encoding='utf-8') as f:
        json_objs = json.load(f)
        logger.info(insDt)
        for json_obj in json_objs:
            if retailer == 'tesco':
                Tesco(data=json_obj, ins_ts=datetime.strptime(insDt, '%Y%m%d'))
            elif retailer == 'sainsburys':
                Sainsburys(data=json_obj, ins_ts=datetime.strptime(insDt, '%Y%m%d'))
            elif retailer == 'morrison':
                Morrison(data=json_obj, ins_ts=datetime.strptime(insDt, '%Y%m%d'))
            elif retailer == 'ocado':
                Ocado(data=json_obj, ins_ts=datetime.strptime(insDt, '%Y%m%d'))
            elif retailer == 'asda':
                logger.debug(json_obj)
                Asda(data=json_obj, ins_ts=datetime.strptime(insDt, '%Y%m%d'))
            else:
                logger.error('Invalid retailer name provided')


@orm.db_session
def get_ins_date(retailer):
    if retailer == 'tesco':
        result = orm.select(a.ins_ts for a in Tesco).max()
        if result is None:
            result = '20180215'
        else:
            result = datetime.strftime(orm.select(a.ins_ts for a in Asda).max() + timedelta(days=1), '%Y%m%d')
    if retailer == 'sainsburys':
        result = orm.select(a.ins_ts for a in Sainsburys).max()
        if result is None:
            result = '20180215'
        else:
            result = datetime.strftime(orm.select(a.ins_ts for a in Asda).max() + timedelta(days=1), '%Y%m%d')
    if retailer == 'morrison':
        result = orm.select(a.ins_ts for a in Morrison).max()
        if result is None:
            result = '20180220'
        else:
            result = datetime.strftime(orm.select(a.ins_ts for a in Asda).max() + timedelta(days=1), '%Y%m%d')
    if retailer == 'ocado':
        result = orm.select(a.ins_ts for a in Ocado).max()
        if result is None:
            result = '20180308'
        else:
            result = datetime.strftime(orm.select(a.ins_ts for a in Asda).max() + timedelta(days=1), '%Y%m%d')
    if retailer == 'asda':
        result = orm.select(a.ins_ts for a in Asda).max()
        if result is None:
            result = '20180611'
        else:
            result = datetime.strftime(orm.select(a.ins_ts for a in Asda).max() + timedelta(days=1), '%Y%m%d')
    logger.info(result)
    return result


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-t', '--type', help='Retailer name',
                            required=True)
        args = vars(parser.parse_args())
        retailer = args['type']
        if retailer == 'asdafiles':
            ins_all_files('ASDA')
            sys.exit(0)
        with orm.db_session:
            fileDate = get_ins_date(retailer)
        logger.info('About to Insert {} for {}'.format(fileDate, retailer))
        if retailer == 'tesco':
            json_file = os.path.abspath('TESC_' + fileDate + '.json')
        elif retailer == 'sainsburys':
            json_file = os.path.abspath('SAINS_' + fileDate + '.json')
        elif retailer == 'morrison':
            json_file = os.path.abspath('MORRI_' + fileDate + '.json')
        elif retailer == 'ocado':
            json_file = os.path.abspath('OCCAD_' + fileDate + '.json')
        elif retailer == 'asda':
            json_file = os.path.abspath('ASDA_' + fileDate + '.json')
        elif retailer == 'asdafiles':
            ins_all_files('ASDA')
        else:
            logger.error("Invalid retailer name provided")
            sys.exit(0)
        logger.info('working on ' + json_file + ' ...')
        logger.info(json_file)
        if os.path.isfile(json_file):
            with orm.db_session:
                ins_data(json_file, fileDate, retailer)
        else:
            logger.error('File: ' + json_file + ' not found...')
    finally:
        logger.info('Activity Complete')
