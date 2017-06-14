#!/bin/bash

psql -U postgres -d cloudbox -h 127.0.0.1 -c "select iot.cal_missing_alarm()"