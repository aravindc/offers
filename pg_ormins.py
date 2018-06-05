from datetime import datetime, timedelta
import uuid
from pony import orm
import json
import logging
from dbconfig import read_pg_config
import argparse
import os
import sys
import glob


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
    files = glob.glob(os.path.abspath(retailer+'_*.json'))
    files.sort(key=os.path.getmtime)
    for f in files:
        insDt = f.split('_')[1].split('.')[0]
        with orm.db_session:
            ins_data(f, insDt, retailer.lower())


@orm.db_session
def ins_data(insFile, insDt, retailer):
    with open(insFile, 'r+', encoding='utf-8') as f:
        json_objs = json.load(f)
        logger.info(insDt)
        for json_obj in json_objs:
            if retailer == 'tesco' or retailer == 'tesc':
                Tesco(data=json_obj, ins_ts=datetime.strptime(insDt, '%Y%m%d'))
            elif retailer == 'sainsburys' or retailer == 'sains':
                Sainsburys(data=json_obj, ins_ts=datetime.strptime(insDt, '%Y%m%d'))
            elif retailer == 'morrison' or retailer == 'morri':
                Morrison(data=json_obj, ins_ts=datetime.strptime(insDt, '%Y%m%d'))
            elif retailer == 'ocado' or retailer == 'occad':
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
            result = datetime.strftime(orm.select(a.ins_ts for a in Tesco).max() + timedelta(days=1), '%Y%m%d')
    if retailer == 'sainsburys':
        result = orm.select(a.ins_ts for a in Sainsburys).max()
        if result is None:
            result = '20180215'
        else:
            result = datetime.strftime(orm.select(a.ins_ts for a in Sainsburys).max() + timedelta(days=1), '%Y%m%d')
    if retailer == 'morrison':
        result = orm.select(a.ins_ts for a in Morrison).max()
        if result is None:
            result = '20180220'
        else:
            result = datetime.strftime(orm.select(a.ins_ts for a in Morrison).max() + timedelta(days=1), '%Y%m%d')
    if retailer == 'ocado':
        result = orm.select(a.ins_ts for a in Ocado).max()
        if result is None:
            result = '20180308'
        else:
            result = datetime.strftime(orm.select(a.ins_ts for a in Ocado).max() + timedelta(days=1), '%Y%m%d')
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
        parser.add_argument('-t', '--type', help='Single or All files',
                            required=True)
        parser.add_argument('-r', '--retailer', help='Retailer Name',
                            required=True)
        args = vars(parser.parse_args())
        filetype = args['type']
        retailer = args['retailer']
        if filetype == 'single':
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
            else:
                logger.error("Invalid retailer name provided")
                sys.exit(0)
            if os.path.isfile(json_file):
                with orm.db_session:
                    ins_data(json_file, fileDate, retailer)
            else:
                logger.error('File: ' + json_file + ' not found...')
        elif filetype == 'all':
            if retailer == 'tesco':
                ins_all_files('TESC')
            elif retailer == 'sainsburys':
                ins_all_files('SAINS')
            elif retailer == 'morrison':
                ins_all_files('MORRI')
            elif retailer == 'ocado':
                ins_all_files('OCCAD')
            elif retailer == 'asda':
                ins_all_files('ASDA')
            else:
                logger.error("Invalid retailer name provided")
                sys.exit(0)
        else:
            logger.error("Invalid file type provided")
            sys.exit(0)
    finally:
        logger.info('Activity Complete')
