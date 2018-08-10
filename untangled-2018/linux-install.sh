#!/bin/bash

# minimum of python 3.7 required
pip3.7 install --user -r requirements.txt

if [ ! -e lib/config.py ]; then
  echo What would you like the hostname to be?
  read hostinput
  echo "HOSTNAME = '$hostinput'" > lib/config.py
fi