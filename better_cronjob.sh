#!/bin/bash
cd ~/Work/cluster_log/
. ~/.bash_profile
python better_logger.py >> better_error.log 2>&1
