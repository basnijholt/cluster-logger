#!/bin/bash
cd ~/Work/cluster_log/
. ~/.bash_profile
python logger.py --clean_db >> error.log 2>&1
