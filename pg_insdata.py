import psycopg2
from dbconfig import read_pg_config
import logging
import os
import os.path
import argparse
import sys


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
            qrystr = """SELECT to_char(max(ins_ts) + interval '1 day',
               'YYYYMMDD') as insdt from tesco"""
            cursor.execute(qrystr)
            row = cursor.fetchone()
            retval = row[0]
            logger.info(retval)
            if retval is None:
                retval = '20180215'
        elif tabname == 'sainsburys':
            qrystr = """SELECT to_char(max(ins_ts) + interval '1 day',
               'YYYYMMDD') as insdt from sainsburys"""
            cursor.execute(qrystr)
            row = cursor.fetchone()
            retval = row[0]
            logger.info(retval)
            if retval is None:
                retval = '20180215'
        elif tabname == 'morrison':
            qrystr = """SELECT to_char(max(ins_ts) + interval '1 day',
               'YYYYMMDD') as insdt from morrison"""
            cursor.execute(qrystr)
            row = cursor.fetchone()
            retval = row[0]
            logger.info(retval)
            if retval is None:
                retval = '20180220'
        elif tabname == 'ocado':
            qrystr = """SELECT to_char(max(ins_ts) + interval '1 day',
               'YYYYMMDD') as insdt from ocado"""
            cursor.execute(qrystr)
            row = cursor.fetchone()
            retval = row[0]
            logger.info(retval)
            if retval is None:
                retval = '20180308'
        elif tabname == 'asda':
            qrystr = """SELECT to_char(max(ins_ts) + interval '1 day',
               'YYYYMMDD') as insdt from asda"""
            cursor.execute(qrystr)
            row = cursor.fetchone()
            retval = row[0]
            logger.info(retval)
            if retval is None:
                retval = '20180611'
    except Exception as e:
        logger.error(e)
    finally:
        cursor.close()
    logger.info(str(retval))
    return str(retval)


def ins_data(conxn, type, json_file):
    try:
        cursor = conxn.cursor()
        temp_str = os.path.splitext(json_file)[0]
        end = None
        ins_dt = temp_str[temp_str.find('_') + 1:end]

        logger.info(json_file)
        # Read in the file
        with open(json_file, 'r', encoding='utf-8') as file:
            filedata = file.read()
        # Replace the target string
        filedata = filedata.replace('\\"', '')
        # Write the file out again
        output_file = os.path.abspath('temp_file.out')
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(filedata)

        qrystrs = ("""drop table if exists temptab1""",
                   """create table temptab1(values text)""",
                   """copy temptab1 from '""" + output_file + """' """,
                   """delete from temptab1 where values='[' or values=']'""",
                   """insert into """ + type + """ select md5(random()::text
                   ||clock_timestamp()::text)::uuid, replace(values,'},','}'
                   )::json,'""" + ins_dt + """' as values from temptab1""",
                   """drop table if exists temptab1""")

        for qrystr in qrystrs:
            cursor.execute(qrystr)
        conxn.commit()
    except Exception as e:
        logger.error(e)
    finally:
        try:
            os.remove(output_file)
        except OSError:
            pass
        cursor.close()


if __name__ == '__main__':
    try:
        conx = connect()
        parser = argparse.ArgumentParser()
        parser.add_argument('-t', '--type', help='Retailer name',
                            required=True)
        args = vars(parser.parse_args())
        if args['type'] == 'tesco':
            json_file = os.path.abspath('TESC_' + get_file_name(conx,
                                        args['type']) + '.json')
        elif args['type'] == 'sainsburys':
            json_file = os.path.abspath('SAINS_' + get_file_name(conx,
                                        args['type']) + '.json')
        elif args['type'] == 'morrison':
            json_file = os.path.abspath('MORRI_' + get_file_name(conx,
                                        args['type']) + '.json')
        elif args['type'] == 'ocado':
            json_file = os.path.abspath('OCCAD_' + get_file_name(conx,
                                        args['type']) + '.json')
        elif args['type'] == 'asda':
            json_file = os.path.abspath('ASDA_' + get_file_name(conx,
                                        args['type']) + '.json')
        else:
            logger.error("Invalid retailer name provided")
            conx.close()
            sys.exit(0)
        logger.info('working on ' + json_file + ' ...')
        logger.info(json_file)
        if os.path.isfile(json_file):
            ins_data(conx, args['type'], json_file)
        else:
            logger.error('File: ' + json_file + ' not found...')
    finally:
        conx.close()
