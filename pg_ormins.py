from datetime import datetime
import uuid
from pony import orm
import json
import logging
from dbconfig import read_pg_config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

params = read_pg_config()

db = orm.Database()
db.bind(provider='postgres', user=params['user'], password=params['password'],
        host=params['host'], database=params['database'])


class morrison(db.entity):
    id = orm.PrimaryKey(uuid.UUID, default=uuid.uuid4, auto=True)
    data = orm.Required(orm.Json)
    ins_ts = orm.Required(datetime)


class ocado(db.entity):
    id = orm.PrimaryKey(uuid.UUID, default=uuid.uuid4, auto=True)
    data = orm.Required(orm.Json)
    ins_ts = orm.Required(datetime)


class sainsburys(db.entity):
    id = orm.PrimaryKey(uuid.UUID, default=uuid.uuid4, auto=True)
    data = orm.Required(orm.Json)
    ins_ts = orm.Required(datetime)


class tesco(db.entity):
    id = orm.PrimaryKey(uuid.UUID, default=uuid.uuid4, auto=True)
    data = orm.Required(orm.Json)
    ins_ts = orm.Required(datetime)


class asda(db.entity):
    id = orm.PrimaryKey(uuid.UUID, default=uuid.uuid4, auto=True)
    data = orm.Required(orm.Json)
    ins_ts = orm.Required(datetime)


sql_debug(True)
db.generate_mapping(create_tables=True)


@db_session
def ins_data(insFile, insDt, retailer):
    with open(insfile, 'r+') as f:
        json_objs = json.load(f)
        for json_obj in json_objs:
            if retailer == 'tesco':
                tesco(data_json=json_obj, ins_ts=insDt)
            elif retailer == 'sainsburys':
                sainsburys(data_json=json_obj, ins_ts=insDt)
            elif retailer == 'morrison':
                morrison(data_json=json_obj, ins_ts=insDt)
            elif retailer == 'ocado':
                ocado(data_json=json_obj, ins_ts=insDt)
            elif retailer == 'asda':
                asda(data_json=json_obj, ins_ts=insDt)
            else:
                logger.error('Invalid retailer name provided')


@db_session
def get_ins_date(retailer):
    if retailer == 'tesco':
        result = asda.select_by_sql("SELECT to_char(max(ins_ts) + interval '1 day', 'YYYYMMDD') as insdt from tesco")
        if result is None:
            result = '20180215'
    if retailer == 'sainsburys':
        result = asda.select_by_sql("SELECT to_char(max(ins_ts) + interval '1 day', 'YYYYMMDD') as insdt from sainsburys")
        if result is None:
            result = '20180215'
    if retailer == 'morrison':
        result = asda.select_by_sql("SELECT to_char(max(ins_ts) + interval '1 day', 'YYYYMMDD') as insdt from morrison")
        if result is None:
            result = '20180220'
    if retailer == 'ocado':
        result = asda.select_by_sql("SELECT to_char(max(ins_ts) + interval '1 day', 'YYYYMMDD') as insdt from ocado")
        if result is None:
            result = '20180308'
    if retailer == 'asda':
        result = asda.select_by_sql("SELECT to_char(max(ins_ts) + interval '1 day', 'YYYYMMDD') as insdt from asda")
        if result is None:
            result = '20180611'
    return result


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-t', '--type', help='Retailer name',
                            required=True)
        args = vars(parser.parse_args())
        fileDate = get_file_name(args['type'])
        retailer = args['type']
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
        logger.info('working on ' + json_file + ' ...')
        logger.info(json_file)
        if os.path.isfile(json_file):
            with orm.db_session:
                ins_data(json_file, fileDate, retailer)
        else:
            logger.error('File: ' + json_file + ' not found...')
