#!/usr/bin/env python

from datetime import datetime
import json
import os
import hpc05

now = datetime.utcnow()

job_log_file = 'job_log_{}.json'.format(now.strftime("%Y-%m"))

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
