# main/tasks.py
import os
import traceback

import logging
logger = logging.getLogger('admin_log')

from django.conf import settings

import pandas

from imgdownloader.celery import app
from .models import Document
from .utils import connect_to_db, parse_file, write_row_to_db
 
@app.task
def prepare_and_upload_file(file_id):
    
    document = Document.objects.get(id=file_id)
    document.status = 1
    document.save()
    # Step 1: connect to DB
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
    if not isinstance(data, pandas.core.frame.DataFrame):
        logger.info(f'File {document.id}, was not succesfully uploaded; error while parsing.')
        document.status = -1
        document.error = f"Unable to parse file; check format, error {data}."
        document.log += f"Step 2: Parsing file is failed: check file. Error {data}.\n"
        document.save()
        return None
    else:
        document.log += f"Step 2: Parsing file {document.file_type} is succeed: continue.\n"
        document.save()
    # Step 4: write all to table
    status, err, sql = write_row_to_db(document.db_type, conn, document.table_name, data)
    if not status:
        logger.info(f'File {document.id}, was not succesfully uploaded; error while inserting to DBMS, sql {sql}, err {err}.')
        document.status = -1
        document.error = err
        document.log += f"Step 3: Inserting row '{sql}' error {err}.\n"
        document.save()
        return None
    logger.info(f'File {document.id}, was succesfully uploaded to DBMS by user {document.user.username}!')
    document.log += f"Step 3: Inserting rows succeed!.\n"
    document.status = 2
    document.document = None
    document.save()
    return None

