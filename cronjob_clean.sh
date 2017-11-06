#!/bin/bash
cd  /home/cluster_logger/cluster-logger-master
python logger.py --clean_db >> error.log 2>&1
