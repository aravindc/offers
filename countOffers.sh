#!/bin/bash

STARTDATE="2020-01-01"
ENDDATE="2020-06-30"

start=$(date -d $STARTDATE +%s)
end=$(date -d $ENDDATE +%s)

d="$start"

echo $d
echo $end
while [[ $d -le $end ]]
do
    x=$(date -d @$d +%Y%m%d)
    cnt=$(cat SAINS_$x.json | jq '.[].productid' | wc -l)
    echo $x-$cnt >> /tmp/sainsCount.txt
    d=$(( $d + 86400 ))
done
