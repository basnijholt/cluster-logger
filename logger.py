#!/usr/bin/env python

"""Add this as a crobjob at hpc1:
*/15 * * * * /home/bnijholt/anaconda3/bin/python /home/bnijholt/Dropbox/Work/cluster_log/logger.py >> /home/bnijholt/Dropbox/Work/cluster_log/logger.log 2>&1
or add this as a crobjob at hpc05:
*/15 * * * * /home/basnijholt/anaconda3/bin/python /home/basnijholt/Dropbox/Work/cluster_log/logger.py --local=True >> /home/basnijholt/Dropbox/Work/cluster_log/logger.log 2>&1
"""
from datetime import datetime
import json
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--local', nargs='?', const=False, type=bool)
args = parser.parse_args()

now = datetime.utcnow()

fname = 'job_log_{}.json'.format(now.strftime("%Y-%m"))
folder = os.path.expanduser('~/Dropbox/Work/cluster_log/')
job_log_file = os.path.join(folder, fname)

if args.local:
    # If run locally at hpc05
    import subprocess
    out = subprocess.check_output("qstat -ea".split()).decode('utf-8').split('\n')
else:
    # If run via ssh
    import hpc05
    ssh = hpc05.ssh_utils.setup_ssh()
    stdin, stdout, sterr = ssh.exec_command('qstat -ea')
    out = stdout.readlines(), sterr.readlines()

cols = ['Job ID', 'Username', 'Queue', 'Jobname', 'SessID', 'NDS', 'TSK', 
        'Required Memory', 'Required Time', 'S', 'Elapsed Time']
lines = out[0][5:]
processes = []
for line in lines:
    processes.append({key: val for key, val in zip(cols, line.split())})
    process = processes[-1]
    process['current_time'] = datetime.timestamp(now)
    try:
        h, m, s = process['Elapsed Time'].split(':')
        total_seconds = 3600 * int(h) + 60 * int(m) + int(s)
    except:
        total_seconds = 0
    try:
        num_cores = int(process['TSK'])
    except ValueError:
        num_cores = 1
    process['num_cores'] = num_cores
    process['running_time'] = total_seconds

try:
    with open(job_log_file, 'r') as f:
        job_log = json.load(f)
except FileNotFoundError:
    with open(job_log_file, 'w') as f:
        job_log = {}
        json.dump(job_log, f)

for process in processes:
    if process['S'] == 'R':
        key = " ".join([process['Job ID'], process['Username'], process['Jobname']])
        info = (process['current_time'], process['running_time'], process['num_cores'])
        try:
            job_log[key].append(info)
        except KeyError:
            job_log[key] = []
            job_log[key].append(info)

with open(job_log_file, 'w') as f:
    json.dump(job_log, f)
