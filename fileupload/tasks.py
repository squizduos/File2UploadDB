# main/tasks.py
 
import logging
logger = logging.getLogger('admin_log')

from imgdownloader.celery import app
from .models import Document
from .utils import connect_to_db, parse_file, check_table, write_row_to_db
 
@app.task
def prepare_and_upload_file(file_id):
    
    document = Document.objects.get(id=file_id)
    document.status = 1
    document.save()
    # Step 1: connect to DB
    try:
        conn, err = connect_to_db(
            document.db_type,
            document.db_host,
            document.db_port, 
            document.db_name, 
            document.db_username, 
            document.db_password,
            document.db_sid
        )
        if err:
            logger.info(f'Remote DBMS connection was not estabilished (server {document.db_host}, error {err})')
            document.log += f"Step 1: Remote DBMS connection was not estabilished; error {err}\n"
            document.status = -1
            document.error = err
            document.save()
            return None
        else:
            logger.info(f'Remote DBMS connection was estabilished (server {document.db_host})')
            document.log += f"Step 1: Remote DBMS connection was estabilished.\n"
            document.save()
        # Step 2: parse file to dictonary
        data = parse_file(
            document.file_type, 
            document.document.path,
            document.file_header_line,
            document.file_separator
        )
        if not isinstance(data, list):
            document.status = -1
            document.error = f"Unable to parse file; check format."
            document.log += f"Step 2: Parsing file is failed: check file.\n"
            document.save()
            return None
        else:
            document.log += f"Step 2: Parsing file {document.file_type} is succeed: continue.\n"
            document.save()
        # Step 3: checking fields in table
        all_contains, columns_in_table = check_table(document.db_type, conn, document.table_name, list(data[0].keys()))
        if not all_contains:
            document.status = -1
            document.error = "Not all required fields are in table; please fix it"
            document.log += f"Step 3: Not all required fields are in table; table contains next fields: {columns_in_table}, our table contains next fields: {list(data[0].keys())}"
            document.save()
            return None
        else:
            document.log += f"Step 3: All required fields are in table. Waiting to start uploading.\n"
            document.save()
        # Step 4: write all to table
        loaded_rows = 0
        all_rows = len(data)
        for row in data:
            status, err, sql = write_row_to_db(document.db_type, conn, document.table_name, row)
            if not status:
                document.status = -1
                document.error = err
                document.log += f"Step 4: Inserting row '{sql}' error {err}.\n"
                document.save()
                return None
            if int(loaded_rows / all_rows * 100.0) > document.uploading_percent:
                document.uploading_percent =  int(loaded_rows / all_rows * 100.0)
                document.save()
            loaded_rows += 1
        document.log += f"Step 4: Inserting rows succeed!.\n"
        document.status = 2
        document.document = None
        document.save()
        return None
    except Exception as e:
        document.status = -1
        document.error = err
        document.save()
        return None
