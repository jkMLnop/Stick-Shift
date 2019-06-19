#!/bin/sh

sudo apt update
sudo apt -y install python3-pip
pip install pyspark --user
pip3 install findspark --user

