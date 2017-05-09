#!/usr/bin/env python

from collections import Counter
import subprocess

x = subprocess.check_output('qstat -ea'.split())
out = x.decode('utf-8').split('\n')

cols = ['Job ID', 'Username', 'Queue', 'Jobname', 'SessID', 'NDS', 'TSK',
        'Required Memory', 'Required Time', 'S', 'Elapsed Time']

lines = out[5:-1]
processes = []
for line in lines:
    processes.append({key: val for key, val in zip(cols, line.split())})
    process = processes[-1]
    try:
        num_cores = int(process['TSK'])
    except ValueError:
        num_cores = 1
    process['num_cores'] = num_cores

cnt = Counter()

for process in processes:
    if process['S'] == 'R':
        user = process['Username']
        try:
            num_cores = int(process['TSK'])
        except ValueError:
            num_cores = 1
        cnt[user] += num_cores

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

total_in_use = sum(cnt.values())

LOCALnodeload = x = subprocess.check_output('LOCALnodeload.pl'.split()).decode('utf-8').split('\n')[2:-1]
total_cores = sum(int(i.split()[1]) for i in LOCALnodeload)
free_cores = total_cores - total_in_use
print(bcolors.WARNING + 'Total in cores in use: {}, free: {}\n'.format(total_in_use, free_cores) + bcolors.ENDC)
for user, num_cores in sorted(cnt.items(), key=lambda x: -x[1]):
    print(bcolors.OKGREEN + '{} uses {} cores'.format(user, num_cores) + bcolors.ENDC)
