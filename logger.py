#!/usr/bin/env python

import argparse
from collections import defaultdict
from datetime import datetime, timedelta
import gzip
import os
import pickle

import hpc05
from pytz import timezone


tz = timezone('Europe/Amsterdam')  # timezone in the Netherlands
tz_offset = tz.utcoffset(datetime.now()).seconds // 3600
now = datetime.now(tz)


def get_qstat():
    ssh = hpc05.ssh_utils.setup_ssh()
    stdin, stdout, sterr = ssh.exec_command('qstat -ea')
    out = stdout.readlines(), sterr.readlines()
    lines = out[0][5:]
    return lines


def get_total_cores():
    ssh = hpc05.ssh_utils.setup_ssh()
    stdin, stdout, sterr = ssh.exec_command('LOCALnodeload.pl')
    out, err = stdout.readlines(), sterr.readlines()
    lines = out[2:]
    return sum(int(line.split()[1]) for line in lines)


def print_current_usage():
    lines = get_qstat()
    processes = [process_line(line) for line in lines]
    processes = [p for p in processes if p is not None]  # Filter out `None`s

    stat = defaultdict(int)
    for p in processes:
        stat[p['Username']] += p['num_cores']

    class bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

    total_in_use = sum(v for v in stat.values())

    total_cores = get_total_cores()

    free_cores = total_cores - total_in_use
    print(bcolors.WARNING + 'Total in cores in use: {}, free: {}\n'.format(
        total_in_use, free_cores) + bcolors.ENDC)
    for user, num_cores in sorted(stat.items(), key=lambda x: -x[1]):
        print(bcolors.OKGREEN + '{} uses {} cores'.format(user, num_cores) + bcolors.ENDC)


def parse_line(line):
    cols = ['Job ID', 'Username', 'Queue', 'Jobname', 'SessID', 'NDS', 'TSK',
            'Required Memory', 'Required Time', 'S', 'Elapsed Time']
    process_dict = {key: val for key, val in zip(cols, line.split())}
    return process_dict


def get_num_processors(process):
    try:
        num_cores = int(process['TSK'])
    except ValueError:
        num_cores = 1
    return num_cores


def set_elapsed_time(process):
    try:
        h, m, s = process['Elapsed Time'].split(':')
        total_seconds = 3600 * int(h) + 60 * int(m) + int(s)
    except:
        total_seconds = 0
    return total_seconds


def filter_dict(process):
    to_save = ['Job ID', 'Jobname', 'SessID', 'Username',
               'current_time', 'num_cores', 'cpu_time']
    filtered_process = {k: process[k] for k in to_save}
    return filtered_process


def process_line(line):
    process = parse_line(line)
    if process['S'] == 'R':
        process['current_time'] = datetime.timestamp(now)
        process['num_cores'] = get_num_processors(process)
        process['cpu_time'] = set_elapsed_time(process)
        return filter_dict(process)


def save_processes(processes, fname, append=True):
    mode = 'ab' if append else 'wb'
    with gzip.open(fname, mode) as pfile:
        for p in processes:
            pickle.dump(p, pfile)


def load_processes(fname):
    processes = []
    with gzip.open(fname, 'rb') as f:
        while True:
            try:
                process = pickle.load(f)
            except EOFError:
                break
            except pickle.UnpicklingError:
                # If an UnpicklingError happens overwrite the database.
                save_processes(processes, fname, append=False)
                break
            processes.append(process)
    return processes


def older_than(process, days=30):
    time = date_from_process(process)
    return time < now - timedelta(days=days)


def date_from_process(process):
    return datetime.fromtimestamp(process['current_time'], tz)


def clean_database(database_fname, days=60):
    processes = load_processes(database_fname)
    to_archive = defaultdict(list)
    keep = []
    for process in processes:
        date = date_from_process(process)
        if older_than(process, days=days):
            key = date.strftime("%Y-%m")
            to_archive[key].append(process)
        else:
            keep.append(process)

    for fname, processes in to_archive.items():
        os.makedirs('archive', exist_ok=True)
        fname = 'archive/' + fname + '.p'
        append = os.path.isfile(fname)
        save_processes(processes, fname, append)

    save_processes(keep, database_fname, append=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Log qstat or clean its database.')
    parser.add_argument('-f', '--fname', type=str, default='database.p')
    parser.add_argument('-c', '--clean_db', action='store_true')
    args = parser.parse_args()

    database_fname = args.fname

    if args.clean_db:
        clean_database(database_fname)

    else:
        lines = get_qstat()

        processes = [process_line(line) for line in lines]
        processes = [p for p in processes if p is not None]  # Filter out `None`s

        save_processes(processes, database_fname, append=True)
