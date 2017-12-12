#!/bin/bash -x

while read line
do
    if [ $(echo $line | egrep ^# | wc -l) -eq 0 ]
    then
        db=$(echo $line | cut -d ";" -f 1)
        collection=$(echo $line | cut -d ";" -f 2)
        file=$(echo $line | cut -d ";" -f 3)
        mongoimport --db $db --collection $collection --file $file
    fi
done < /docker-entrypoint-initdb.d/imports.txt