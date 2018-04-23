#!/bin/sh

python3 pg_insdata.py -t tesco
python3 pg_insdata.py -t sainsburys
python3 pg_insdata.py -t morrison
python3 pg_insdata.py -t ocado

