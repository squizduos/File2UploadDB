FROM python:3.6
RUN apt-get update
RUN apt-get install libaio1 libaio-dev
WORKDIR /tmp
RUN wget -q https://github.com/brmzkw/cx_oracle/releases/download/oracle-instantclient12.1/oracle-instantclient12.1-basic_12.1.0.2.0-2_amd64.deb
RUN wget -q https://github.com/brmzkw/cx_oracle/releases/download/oracle-instantclient12.1/oracle-instantclient12.1-devel_12.1.0.2.0-2_amd64.deb
RUN wget -q https://github.com/brmzkw/cx_oracle/releases/download/oracle-instantclient12.1/oracle-instantclient12.1-sqlplus_12.1.0.2.0-2_amd64.deb
RUN dpkg -i /tmp/*.deb
RUN rm -rf /tmp/*.deb
ENV LD_LIBRARY_PATH=/usr/lib/oracle/12.1/client64/lib:$LD_LIBRARY_PATH
ENV PYTHONBUFFERED 1
ENV NLS_LANG RUSSIAN_RUSSIA.AL32UTF8
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code
