#!/bin/sh

rsync -azP ara@192.95.0.118:/opt/offers/*.json /home/ara/offers

#python3 pg_insdata.py -t tesco
#python3 pg_insdata.py -t sainsburys
#python3 pg_insdata.py -t morrison
#python3 pg_insdata.py -t ocado
#python3 pg_insdata.py -t asda

#python3 pg_ormins.py -t single -r tesco
#python3 pg_ormins.py -t single -r sainsburys
#python3 pg_ormins.py -t single -r morrison
#python3 pg_ormins.py -t single -r ocado
#python3 pg_ormins.py -t single -r asda

python3 pg_ormins.py -t all -r tesco
python3 pg_ormins.py -t all -r sainsburys
python3 pg_ormins.py -t all -r morrison
python3 pg_ormins.py -t all -r ocado
python3 pg_ormins.py -t all -r asda

