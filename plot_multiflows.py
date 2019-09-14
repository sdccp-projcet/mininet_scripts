#!/usr/bin/python
import argparse
import re
import os
import matplotlib.pyplot as plt
from file_process import *

RYU_LOG_FILE = "/home/lam/Projects/sdccp/ryu/build/flow_log.txt"
OUTPUT_IMG = "build/multi_flows.png"


def plot_multiflows(f, out, xlim=None):
    with open(f) as fs:
        data = fs.readlines()
    data = [x1.split() for x1 in data]
    start_time = float(data[0][0])

    time_sendingrates = {}
    for line in data:
        if line[1] > '0':
            num = int(line[1])
            for i in range(0, num):
                time_sendingrates.setdefault(line[2+i*2], [])
                time_sendingrates[line[2+i*2]].append([float(line[0]) - start_time, float(line[3+i*2]) / 1000000])

    plt.figure()
    for user in time_sendingrates.keys():
        t = [i[0] for i in time_sendingrates[user]]
        s = [i[1] for i in time_sendingrates[user]]
        plt.plot(t, s)

    plt.savefig(out)
    plt.show()


parser = argparse.ArgumentParser()
parser.add_argument('--xlim', '-x',
                    help="xaxis range limit",
                    action="store",
                    dest="xlim")


if __name__ == '__main__':
    args = parser.parse_args()
    log_file = RYU_LOG_FILE
    output_img = OUTPUT_IMG
    if args.xlim:
        plot_multiflows(log_file, output_img, xlim=int(args.xlim))
    else:
        plot_multiflows(log_file, output_img)
