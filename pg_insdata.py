import psycopg2
from dbconfig import read_pg_config
import logging
import os
import os.path
import argparse
import sys
import json


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    cur = None
    try:
        # read connection parameters
        params = read_pg_config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        #  execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
    except Exception as e:
        logger.error(e)
    finally:
        cur.close()
    return conn


def get_file_name(conxn, tabname):
    try:
        cursor = conxn.cursor()
        if tabname == 'tesco':
            qrystr = """SELECT date_format(DATE_ADD(max(ins_ts), INTERVAL 1 DAY),'%Y%m%d') from tesco"""
            cursor.execute(qrystr)
            row = cursor.fetchone()
            retval = row[0]
            logger.info(retval)
            if retval is None:
                retval = '20180215'
        elif tabname == 'sainsburys':
            qrystr = """SELECT date_format(DATE_ADD(max(ins_ts), INTERVAL 1 DAY),'%Y%m%d') from sainsburys"""
            cursor.execute(qrystr)
            row = cursor.fetchone()
            retval = row[0]
            logger.info(retval)
            if retval is None:
                retval = '20180215'
        elif tabname == 'morrison':
            qrystr = """SELECT date_format(DATE_ADD(max(ins_ts), INTERVAL 1 DAY),'%Y%m%d') from morrison"""
            cursor.execute(qrystr)
            row = cursor.fetchone()
            retval = row[0]
            logger.info(retval)
            if retval is None:
                retval = '20180220'
        elif tabname == 'ocado':
            qrystr = """SELECT date_format(DATE_ADD(max(ins_ts), INTERVAL 1 DAY),'%Y%m%d') from ocado"""
            cursor.execute(qrystr)
            row = cursor.fetchone()
            retval = row[0]
            logger.info(retval)
            if retval is None:
                retval = '20180304'
    except Exception as e:
        logger.error(e)
    finally:
        cursor.close()
    logger.info(str(retval))
    return str(retval)


def ins_data(conxn, type, json_file):
    try:
        cursor = conxn.cursor()
        #  json_data = open(json_file).read()
        temp_str = os.path.splitext(json_file)[0]
        end = None
        ins_dt = temp_str[temp_str.find('_') + 1:end]

        qrystrs = ("""create table temptab1(values text)""",
                   """copy temptab1 from '""" + json_file + """' """,
                   """delete from temptab1 where values='[' or values=']'""",
                   """insert into """ + type + """ select md5(random()::text || clock_timestamp()::text)::uuid, replace(values,'},','}')::json,'"""
                   + ins_dt + """' as values from temptab1""",
                   """drop table if exists temptab1""")
        for qrystr in qrystrs:
            cursor.execute(qrystr)
        conxn.commit()
    except Exception as e:
        logger.error(e)
    finally:
        cursor.close()


if __name__ == '__main__':
    try:
        conx = connect()
        parser = argparse.ArgumentParser()
        parser.add_argument('-t', '--type', help='Retailer name', required=True)
        args = vars(parser.parse_args())
        if args['type'] == 'tesco':
            json_file = os.path.expanduser('TESC_' + get_file_name(conx, args['type']) + '.json')
        elif args['type'] == 'sainsburys':
            json_file = os.path.expanduser('SAINS_' + get_file_name(conx, args['type']) + '.json')
        elif args['type'] == 'morrison':
            json_file = os.path.expanduser('MORRI_' + get_file_name(conx, args['type']) + '.json')
        elif args['type'] == 'ocado':
            json_file = os.path.expanduser('OCCAD_' + get_file_name(conx, args['type']) + '.json')
        else:
            logger.error("Invalid retailer name provided")
            conx.close()
            sys.exit(0)
        logger.info('working on ' + json_file + ' ...')
        if os.path.isfile(json_file):
            ins_data(conx, args['type'], json_file)
        else:
            logger.error('File: ' + json_file + ' not found...')
    finally:
        conx.close()
