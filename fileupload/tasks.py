# main/tasks.py
import os, traceback

import logging
logger = logging.getLogger('admin_log')

from django.conf import settings

import pandas

from sqlalchemy import create_engine, types

import celery.states

from imgdownloader.celery import app
from .models import Document
from .utils import chunker

class DocumentTask(celery.Task):
    ignore_result = True
    name = "DocumentTask"

    def run(self, file_id, *args, **kwargs):
        self.file_id = file_id
        self.log = ""
        # Starting task
        self.document = Document.objects.get(id=file_id)
        self.update_on_start()
        # Step 1: connect to DB
        status_string = f"Step 1: Connecting to DBMS..."
        self.update_with_pending(status_string, 0)
        self.conn, err = self.connect_to_db(self.document)
        if err:
            err_string = f'Step 1: connect to DBMS {self.document.db_type} at host {self.document.db_host} is failed; error {err}'
            return self.update_with_error(err_string)
        else:
            status_string = f"Step 1: Remote DBMS connection was estabilished (server {self.document.db_host})."
            self.update_with_pending(status_string, 0)
        # Step 2: parse file to dictonary
        status_string = f"Step 2: Parsing file..."
        self.update_with_pending(status_string, 0)
        data = self.parse_file(self.document)
        if not isinstance(data, pandas.core.frame.DataFrame):
            err_string = f'File {self.document.id}, was not succesfully uploaded; error while parsing; not compartble type {type(data)}'
            return self.update_with_error(err_string)
        else:
            status_string = f"Step 2: Parsing file {self.document.file_type} is succeed."
            self.update_with_pending(status_string, 0)
        # Step 3: write all to table
        status_string = "Step 3: Uploading file to DBMS..."
        self.update_with_pending(status_string, 0)
        chunksize = int(len(data) / 100) # 1%
        for i, cdf in enumerate(chunker(data, chunksize)):
            status, err = self.write_row_to_db(self.document, cdf)
            if not status:
                err_string = f"File {self.document.id}, was not succesfully uploaded; error while inserting to DBMS, err {err}."
                return self.update_with_error(err_string)
            status_string = "Step 3: Uploading file to DBMS..."
            self.update_with_pending(status_string, i)
        return self.update_with_success()

    # def on_success(self, retval, task_id, *args, **kwargs):
    #     state = celery.result.AsyncResult(task_id).info
    #     if retval > 0:
    #         logger.info(f"File {self.file_id} uploading succeed!")
    #         document = Document.objects.get(id=self.file_id)
    #         document.status = 2
    #         document.log = state['log']
    #         document.save()
    #     else:
    #         state = celery.result.AsyncResult(task_id).info
    #         error = state['error']
    #         log = state['log']
    #         logger.info(f"File {self.file_id} uploading faled; error {error}")
    #         document = Document.objects.get(id=self.file_id)
    #         document.status = -1
    #         document.error = error
    #         document.log = log
    #         document.save()            

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.info(f"File {self.file_id} uploading faled; celery error")
        document = Document.objects.get(id=self.file_id)
        self.log += f'Celery error.\n'
        document.error = "Celery error"
        document.log = self.log
        document.status = -1
        document.save()

    def update_with_error(self, err_string):
        logger.info(f"[# Document {self.file_id}] {err_string}")
        self.log += f'{err_string}\n'
        self.document.status = -1
        self.document.error = err_string
        self.document.log = self.log
        self.document.save()
        return -1

    def update_on_start(self):
        self.document.status = 1
        self.document.error = "Process launched"
        self.document.percent = 0
        self.document.save()

    def update_with_pending(self, status_string, percent):
        self.document.error = status_string
        self.document.percent = percent
        self.document.save()

    def update_with_success(self):
        logger.info(f"[# Document {self.file_id}] successfully uploaded!")
        self.document.percent = 100
        self.document.status = 2
        self.document.log = self.log
        self.document.save()
        return 1

    def connect_to_db(self, document):
        if document.db_type == 'PostgreSQL':
            try:
                connection_string = "postgresql://{uname}:{pw}@{ip}:{port}/{db}".format(
                    uname=document.db_username,
                    pw=document.db_password,
                    ip=document.db_host,
                    port=document.db_port,
                    db=document.db_name
                )
                conn = create_engine(connection_string)
                return conn, None
            except Exception as e:
                return None, str(e)
        elif document.db_type == 'Oracle':
            try:
                connection_string = 'oracle+cx_oracle://{uname}:{pw}@{ip}:{port}/{SID}'.format(
                    uname=document.db_username,
                    pw=document.db_password,
                    ip=document.db_host,
                    port=document.db_port,
                    SID=document.db_sid
                )
                conn = create_engine(connection_string)
                return conn, None
            except Exception as e:
                return None, str(e)
        else:
            return None, "Incorrect DB type"

    def parse_file(self, document):
        if document.file_type == 'CSV':
            try:
                data_frame = pandas.read_csv(
                    document.document.path,
                    sep=document.file_separator,
                    header=int(document.file_header_line),
                    keep_default_na=False
                )
                return data_frame
            except Exception as e:
                return str(e)
        elif document.file_type in ['XLS', 'XLSX']:
            try:
                xl = pandas.ExcelFile(document.document.path)
                data_frame = xl.parse(header=int(document.file_header_line))
                indexes_for_drop = [val for val in data_frame.columns if 'Unnamed' in str(val)]
                data_frame = data_frame.drop(indexes_for_drop, axis=1)
                return data_frame
            except Exception as e:
                return str(e)    
        elif document.file_type == 'DTA':
            try:
                data_frame = pandas.read_stata(document.document.path)
                return data_frame
            except Exception as e:
                return str(e)

    def write_row_to_db(self, document, data):
        if document.db_type == 'PostgreSQL':
            try:
                data.to_sql(document.table_name, self.conn, if_exists='append')
            except Exception as e:
                return False, str(e)
            else:
                return True, None
        elif document.db_type == 'Oracle':
            try:
                ntyp = {d: types.VARCHAR(310) for d in data.columns[data.isnull().all()].tolist()}
                to_vc = {c: types.VARCHAR(300) for c in data.columns[data.dtypes == 'object'].tolist()}
                ntyp.update(to_vc)
                data.to_sql(document.table_name, self.conn, if_exists='append', dtype=ntyp, index=False)
            except Exception as e:                
                logger.info(f"[# Document {self.file_id}] error {traceback.format_exc()}, data: {data}")
                return False, str(e)
            else:
                return True, None
        else:
            return False, "Incorrect DB type"
        

app.tasks.register(DocumentTask())
