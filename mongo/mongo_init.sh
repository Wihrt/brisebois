#!/bin/bash

while read line
do
    db=$(echo $line | cut -d ";" -f 1)
    collection=$(echo $line | cut -d ";" -f 2)
    file=$(echo $line | cut -d ";" -f 3)
    mongoimport --db $db -- collection $collection --file $file
done < imports.txt