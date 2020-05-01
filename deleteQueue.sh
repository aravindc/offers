#!/bin/sh
while IFS= read -r line; do
   echo "Deleting $line"
   myline=`echo $line | xargs`
   python3 ~/rabbitmqadmin.py delete queue name="${myline}"
done < /tmp/q.txt
