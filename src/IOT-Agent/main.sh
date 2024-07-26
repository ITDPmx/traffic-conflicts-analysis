#!/bin/bash

#Path to actual script
cd "$(dirname "$0")"
export PYTHONPATH='/home/cloudera/HDPyspark/Project/HDPTableCounter'
#App go!
python main.py
