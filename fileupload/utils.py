import subprocess
import re

def file_read_from_tail(fname, lines):
    proc = subprocess.Popen(['tail', str(-1*lines), fname], stdout=subprocess.PIPE)
    lines = proc.stdout.readlines()
    return ''.join((s.decode('utf-8') for s in lines))

def chunker(seq, size):
    # from http://stackoverflow.com/a/434328
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def encode_db_connection(db_type="", db_username="", db_password="", db_host="", db_port="", db_sid="", db_name="", *args, **kwargs):
    DB_TYPE = {
        "PostgreSQL": "postgres",
        "Oracle": "oracle+cx_oracle"
    }
    return f"{DB_TYPE[db_type]}://{db_username}:{db_password}@{db_host}:{db_port}/{db_sid if db_type == 'Oracle' else db_name}" if len(db_host) > 0 else ""

def decode_db_connection(db_connection):
    DB_TYPE = {
        "postgres": "PostgreSQL",
        "oracle+cx_oracle": "Oracle"
    }
    regex = "(?P<db_type>.*):\/\/(?P<db_username>.*):(?P<db_password>.*)@(?P<db_host>.*):(?P<db_port>.*)\/(?P<db_name>.*)"
    regex_expression = re.compile(regex)
    for el in regex_expression.finditer(db_connection):
        result = el.groupdict()
    # Define db sid
    result['db_type'] = DB_TYPE[result['db_type']]
    result['db_sid'] = result['db_name'] if result['db_type'] == "Oracle" else "not applicable"
    result['db_name'] = "not applicable" if result['db_type'] == "Oracle" else result['db_name']
    return result

