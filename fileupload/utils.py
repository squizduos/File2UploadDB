import subprocess

import psycopg2
import cx_Oracle

import pandas

import logging
logger = logging.getLogger('admin_log')


def file_read_from_tail(fname, lines):
    proc = subprocess.Popen(['tail', str(-1*lines), fname], stdout=subprocess.PIPE)
    lines = proc.stdout.readlines()
    return ''.join((s.decode('utf-8') for s in lines))


def connect_to_db(db_type, host, port, database, user, password, sid=None):
    if db_type == 'PostgreSQL':
        params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
        try:
            conn = psycopg2.connect(**params)
            return conn, None
        except Exception as e:
            return None, str(e)
    elif db_type == 'Oracle':
        # conn_str = f'{user}/{password}@{host}:{port}/{database}'
        try:
            dsn_tns = cx_Oracle.makedsn(host, port, sid)
            conn = cx_Oracle.connect(user, password, dsn_tns)
            return conn, None
        except Exception as e:
            return None, str(e)
    else:
        return None, "Incorrect DB type"

def parse_file(file_type, file, header_line, separator):
    if file_type == 'CSV':
        try:
            data_frame = pandas.read_csv(file, sep=separator, header=int(header_line))
            data = data_frame.to_dict(orient='records')
            return data
        except Exception as e:
            return str(e)
    elif file_type == 'XLS' or file_type == 'XLSX':
        try:
            data_frame = pandas.read_excel(file, header=int(header_line))
            indexes_for_drop = [val for val in data_frame.columns if 'Unnamed' in val]
            data_frame = data_frame.drop(indexes_for_drop, axis=1)
            data = data_frame.to_dict(orient='records')
            return data
        except Exception as e:
            return None    
    elif file_type == 'DAT':
        return None

def check_table(db_type, conn, table_name, columns):
    cursor = conn.cursor()
    if db_type == 'PostgreSQL':
        cursor.execute(f"select column_name from information_schema.columns where table_schema = 'public' and table_name='{table_name}'")
        column_names = [row[0] for row in cursor]
    elif db_type == 'Oracle':
        r = cursor.execute(f"select * from {table_name}")
        column_names = [row[0] for row in cursor.description]
    else:
        column_names = []
    cursor.close()
    if all(elem in column_names for elem in columns):
        return True, []
    else:
        return False, column_names

def convert_name_to_string(el):
    return '"%s"' % str(el)

def convert_type_to_string(el):
    if isinstance(el, bool):
        return "'true'" if el else "'false'"
    elif isinstance(el, int):
        return str(el)
    else:
        return '\'%s\'' % str(el.replace("\'", "\'\'"))

def write_row_to_db(db_type, conn, table_name, columns):
    column_names = []
    column_values = []
    for key, value in columns.items():
        column_names.append(key)
        column_values.append(value)
    cursor = conn.cursor()
    if db_type == 'PostgreSQL':
        sql = "INSERT INTO " + table_name + " (" + ','.join(column_names) + ") VALUES (" + ','.join([el for key in column_values]) + ")"
        try:
            cursor.execute(sql, column_values)
            conn.commit()
            cursor.close()
        except Exception as e:
            return False, str(e), sql
        else:
            return True, None, None
    elif db_type == 'Oracle':
        sql = "INSERT INTO " + table_name + " (" + ','.join(
            [convert_name_to_string(el) for el in column_names]
        ) + ") VALUES (" + ', '.join(
            [convert_type_to_string(el) for el in column_values]
        ) + ")"
        try:
            cursor.execute(sql)
            conn.commit()
            cursor.close()
        except Exception as e:
            return False, str(e), sql
        else:
            return True, None, None
    else:
        return False, "Incorrect DB type", None
    