from mysql.connector import MySQLConnection
from mysql.connector import Error
from dbconfig import read_db_config
import logging
import os
import os.path
import argparse
import sys
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def connect():
    """ Connect to Mysql databse """
    db_config = read_db_config()
    try:
        conxn = MySQLConnection(**db_config)
        if conxn.is_connected():
            logger.info('Connected to database')
    except Error as e:
        logger.error(e)
    # finally:
    #    conxn.close()
    #    logger.info('Connection Closed')
    return conxn


def sains_ins_data(conxn, json_file):
    try:
        cursor = conxn.cursor()
        json_data = open(json_file).read()
        temp_str = os.path.splitext(json_file)[0]
        end = None
        ins_dt = temp_str[temp_str.find('_') + 1:end]
        qrystr = """INSERT INTO sains(productid, imgsrcl, productdesc, producturl, priceunit, offerdesc, ins_ts) VALUES(%s, %s, %s, %s, %s, %s, %s)"""
        for item in json.loads(json_data):
            if 'priceunit' not in item:
                item['priceunit'] = 0
            cursor.execute(qrystr, (item['productid'], 'https:' + item['imgsrcl'], item['productdesc'], item['producturl'], item['priceunit'], item['offerdesc'], ins_dt))
        conxn.commit()
    except Error as e:
        logger.error(e)
    finally:
        cursor.close()


def tesc_ins_data(conxn, json_file):
    try:
        cursor = conxn.cursor()
        json_data = open(json_file).read()
        temp_str = os.path.splitext(json_file)[0]
        end = None
        ins_dt = temp_str[temp_str.find('_') + 1:end]
        qrystr = """INSERT INTO tesco(productid, productdesc, offerdesc, validitydesc, imgsrc90, imgsrc110, imgsrc225, imgsrc540, ins_ts) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        for item in json.loads(json_data):
            cursor.execute(qrystr, item['productid'], item['productdesc'], item['offerdesc'], item['validitydesc'], item['imgsrc90'], item['imgsrc110'], item['imgsrc225'], item['imgsrc540'], ins_dt)
        conxn.commit()
    except Error as e:
        logger.error(e)
    finally:
        cursor.close()


def morri_ins_data(conxn, json_file):
    try:
        cursor = conxn.cursor()
        json_data = open(json_file).read()
        temp_str = os.path.splitext(json_file)[0]
        end = None
        ins_dt = temp_str[temp_str.find('_') + 1:end]
        qrystr = """INSERT INTO morri(productid, productdesc, offerdesc, validitydesc, imgsrc90, imgsrc110, imgsrc225, imgsrc540, ins_ts) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        for item in json.loads(json_data):
            cursor.execute(qrystr, item['productid'], item['productdesc'], item['offerdesc'], item['validitydesc'], item['imgsrc90'], item['imgsrc110'], item['imgsrc225'], item['imgsrc540'], ins_dt)
        conxn.commit()
    except Error as e:
        logger.error(e)
    finally:
        cursor.close()


def occad_ins_data(conxn, json_file):
    try:
        cursor = conxn.cursor()
        json_data = open(json_file).read()
        temp_str = os.path.splitext(json_file)[0]
        end = None
        ins_dt = temp_str[temp_str.find('_') + 1:end]
        qrystr = """INSERT INTO occad(productid, productdesc, offerdesc, validitydesc, imgsrc90, imgsrc110, imgsrc225, imgsrc540, ins_ts) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        for item in json.loads(json_data):
            cursor.execute(qrystr, item['productid'], item['productdesc'], item['offerdesc'], item['validitydesc'], item['imgsrc90'], item['imgsrc110'], item['imgsrc225'], item['imgsrc540'], ins_dt)
        conxn.commit()
    except Error as e:
        logger.error(e)
    finally:
        cursor.close()


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
        elif tabname == 'sains':
            qrystr = """SELECT date_format(DATE_ADD(max(ins_ts), INTERVAL 1 DAY),'%Y%m%d') from sains"""
            cursor.execute(qrystr)
            row = cursor.fetchone()
            retval = row[0]
            logger.info(retval)
            if retval is None:
                retval = '20180215'
        elif tabname == 'morri':
            qrystr = """SELECT date_format(DATE_ADD(max(ins_ts), INTERVAL 1 DAY),'%Y%m%d') from morri"""
            cursor.execute(qrystr)
            row = cursor.fetchone()
            retval = row[0]
            logger.info(retval)
            if retval is None:
                retval = '20180220'
        elif tabname == 'occad':
            qrystr = """SELECT date_format(DATE_ADD(max(ins_ts), INTERVAL 1 DAY),'%Y%m%d') from occad"""
            cursor.execute(qrystr)
            row = cursor.fetchone()
            retval = row[0]
            logger.info(retval)
            if retval is None:
                retval = '20180304'
    except Error as e:
        logger.error(e)
    finally:
        cursor.close()
    logger.info(str(retval))
    return str(retval)


if __name__ == '__main__':
    conx = connect()
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--type', help='Retailer name', required=True)
    args = vars(parser.parse_args())

    if args['type'] == 'tesco':
        json_file = '/opt/offers/TESC_' + get_file_name(conx, 'tesco') + '.json'
    elif args['type'] == 'sains':
        json_file = '/opt/offers/SAINS_' + get_file_name(conx, 'sains') + '.json'
    elif args['type'] == 'morri':
        json_file = '/opt/offers/SAINS_' + get_file_name(conx, 'morri') + '.json'
    elif args['type'] == 'occad':
        json_file = '/opt/offers/SAINS_' + get_file_name(conx, 'occad') + '.json'
    else:
        logger.error("Invalid retailer name provided")
        conx.close()
        sys.exit(0)
    logger.info('working on ' + json_file + ' ...')
    if os.path.isfile(json_file):
        if args['type'] == 'tesco':
            tesc_ins_data(conx, json_file)
        elif args['type'] == 'sains':
            sains_ins_data(conx, json_file)
        elif args['type'] == 'morri':
            morri_ins_data(conx, json_file)
        elif args['type'] == 'occad':
            occad_ins_data(conx, json_file)
    else:
        logger.error('File: ' + json_file + ' not found...')
    conx.close()
