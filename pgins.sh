#!/bin/sh

rsync -azP ara@192.95.0.118:/opt/offers/*.json /home/ara/offers

python3 pg_insdata.py -t tesco
python3 pg_insdata.py -t sainsburys
python3 pg_insdata.py -t morrison
python3 pg_insdata.py -t ocado
python3 pg_insdata.py -t asda
