#!/usr/bin/python
"""
This file plot the figure of link-utilization to loss rate.
It calculates link utilization over the mid-50s (i.e., from 25s to 75s) duration of total 100s runtime.
If the ryu log file does not log enough data in 50s, this file will return without doing anything.
"""
# import argparse
import matplotlib.pyplot as plt
from competition import LOG_FILE as SCRIPT_FILE
from os import listdir
from os.path import isfile, join

# parser = argparse.ArgumentParser()
# parser.add_argument('--expr', '-e',
#                     help="Experiment's name",
#                     action="store",
#                     required=True,
#                     dest="expr")

RYU_LOG_DIR = 'build/utilization2loss/'
CUBIC_DIR = RYU_LOG_DIR + 'cubic/'
FCA_DIR = RYU_LOG_DIR + 'FCA/'
OUTPUT_FILE = RYU_LOG_DIR + 'utilization2loss.png'


def calculate_link_utilization(fle):
    with open(fle, 'r') as f:
        data = f.readlines()
    data = [d.split() for d in data]
    data = filter(lambda x: x[1][0] != '0', data)
    data = map(lambda x: [float(k) for k in x], data)
    start_time = data[0][0]
    time0 = start_time + 25
    time1 = start_time + 75
    data = filter(lambda x: (x[0] > time0) and (x[0] < time1), data)
    # times = [d[0] for d in data]
    # start_time = times[0]
    # times = map(lambda x: x - start_time, times)
    sending_rates = [d[1] for d in data]
    avg_rate = sum(sending_rates) / len(sending_rates)
    return avg_rate


def main():
    cubic_log_files = [join(CUBIC_DIR, f) for f in listdir(CUBIC_DIR) if isfile(join(CUBIC_DIR, f))]
    fca_log_files = [join(FCA_DIR, f) for f in listdir(FCA_DIR) if isfile(join(FCA_DIR, f))]
    cubic_log_files.sort(key=lambda f: float(f.split('/')[-1]))
    fca_log_files.sort(key=lambda f: float(f.split('/')[-1]))
    cubic_avg_sending_rates = [calculate_link_utilization(f) for f in cubic_log_files]
    fca_avg_sending_rates = [calculate_link_utilization(f) for f in fca_log_files]
    cubic_avg_sending_rates = map(lambda s: s / 1000000, cubic_avg_sending_rates)
    fca_avg_sending_rates = map(lambda s: s / 1000000, fca_avg_sending_rates)
    losses = [float(f) for f in listdir(CUBIC_DIR) if isfile(join(CUBIC_DIR, f))]
    losses.sort()
    plt.figure()
    plt.ylim(0, 100)
    plt.xscale('log')
    plt.xlabel('loss rate (log scale)')
    plt.ylabel('throughput (Mbps)')
    plt.plot(losses, cubic_avg_sending_rates, 'r', label='cubic')
    plt.plot(losses, fca_avg_sending_rates, 'b', label='FCA')
    plt.scatter(losses, fca_avg_sending_rates)
    plt.scatter(losses, cubic_avg_sending_rates)
    plt.legend()
    plt.savefig(OUTPUT_FILE)
    plt.show()


if __name__ == '__main__':
    main()
