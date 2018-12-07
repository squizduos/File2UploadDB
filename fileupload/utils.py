import subprocess

import psycopg2
import cx_Oracle

import logging
logger = logging.getLogger('admin_log')


def file_read_from_tail(fname, lines):
    proc = subprocess.Popen(['tail', str(-1*lines), fname], stdout=subprocess.PIPE)
    lines = proc.stdout.readlines()
    return ''.join((s.decode('utf-8') for s in lines))


def connect_to_db(db_type, host, database, user, password):
    if db_type == 'PostgreSQL':
        params = {
            'host': host,
            'database': database,
            'user': user,
            'password': password
        }
        try:
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            logger.info(f'Remote DBMS connection was estabilished (server {host})')
            return cur
        except Exception as e:
            logger.info(f'Remote DBMS connection was not estabilished (server {host}, error {e}')
            return None
    elif db_type == 'Oracle':
        conn_str = u'{user}/{password}@{host}:{port}/{db}'
        try:
            conn = cx_Oracle.connect(conn_str)
            cur = conn.cursor()
            logger.info(f'Remote DBMS connection was estabilished (server {host})')
            return cur
        except Exception as e:
            logger.info(f'Remote DBMS connection was not estabilished (server {host}, error {e}')
            return None
    else:
        return None