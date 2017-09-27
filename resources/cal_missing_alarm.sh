#!/bin/bash

PSQL='/usr/lib/postgresql/9.6/bin/psql'
HOST='127.0.0.1'
USER='postgres'
DB='cloudbox'

date "+%Y-%m-%d %H:%M:%S" >> /opt/runlog.log 2>&1
COMMAND="SELECT iot.cal_missing_alarm()"
${PSQL} -U ${USER} -d ${DB} -h ${HOST}  -c "${COMMAND}" >> /opt/runlog.log 2>&1
