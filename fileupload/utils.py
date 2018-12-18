import subprocess

import pandas

from sqlalchemy import create_engine, types

import logging
logger = logging.getLogger('admin_log')


def file_read_from_tail(fname, lines):
    proc = subprocess.Popen(['tail', str(-1*lines), fname], stdout=subprocess.PIPE)
    lines = proc.stdout.readlines()
    return ''.join((s.decode('utf-8') for s in lines))


def connect_to_db(db_type, host, port, database, user, password, sid=None):
    if db_type == 'PostgreSQL':
        try:
            connection_string = "postgresql://{uname}:{pw}@{ip}:{port}/{db}".format(uname=user, pw=password, ip=host, port=port, db=database)
            conn = create_engine(connection_string)
            return conn, None
        except Exception as e:
            return None, str(e)
    elif db_type == 'Oracle':
        try:
            connection_string = 'oracle+cx_oracle://{uname}:{pw}@{ip}:{port}/{SID}'.format(uname=user, pw=password, ip=host, port=port, db=database)
            conn = create_engine(connection_string)
            return conn, None
        except Exception as e:
            return None, str(e)
    else:
        return None, "Incorrect DB type"

def parse_file(file_type, file, header_line, separator):
    if file_type == 'CSV':
        try:
            data_frame = pandas.read_csv(file, sep=separator, header=int(header_line), keep_default_na=False)
            # data = data_frame.to_dict(orient='records')
            return data_frame
        except Exception as e:
            return str(e)
    elif file_type == 'XLS' or file_type == 'XLSX':
        try:
            xl = pandas.ExcelFile(file)
            data_frame = xl.parse(header=int(header_line))
            indexes_for_drop = [val for val in data_frame.columns if 'Unnamed' in str(val)]
            data_frame = data_frame.drop(indexes_for_drop, axis=1)
            # data = data_frame.to_dict(orient='records')
            return data_frame
        except Exception as e:
            return str(e)    
    elif file_type == 'DAT':
        data_frame = pandas.read_stata(file, keep_default_na=False)
        # data = data_frame.to_dict(orient='records')
        return data_frame

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
        return '\'%s\'' % str(el).replace("\'", "\'\'")

def write_row_to_db(db_type, conn, table_name, data):
    if db_type == 'PostgreSQL':
        try:
            data.to_sql(table_name, conn, chunksize=5000, if_exists='replace')
        except Exception as e:
            return False, str(e), ""
        else:
            return True, None, None
    elif db_type == 'Oracle':
        try:
            ntyp = {d: types.VARCHAR(310) for d in data.columns[data.isnull().all()].tolist()}
            to_vc = {c: types.VARCHAR(300) for c in data.columns[data.dtypes == 'object'].tolist()}
            update_dicts = ntyp.update(to_vc)
            data.to_sql(table_name, conn, chunksize=5000, if_exists='replace', dtype=ntyp)
        except Exception as e:
            return False, str(e), ""
        else:
            return True, None, None
    else:
        return False, "Incorrect DB type", None
    