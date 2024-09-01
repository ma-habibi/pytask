#!/bin/bash

CSV=../vehicles.csv
COLUMNS='kurzname info hu labelIds'

python3.9 test.py $CSV -k $COLUMNS -c
