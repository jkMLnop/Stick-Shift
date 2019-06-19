#!/bin/sh

sudo apt update
sudo apt -y install python3-pip
sudo apt -y install spark
pip install pyspark --user
pip3 install findspark --user
