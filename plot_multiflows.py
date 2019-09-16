#!/usr/bin/python
import argparse
import re
import os
import matplotlib.pyplot as plt
from file_process import *

RYU_LOG_FILE = "/home/lam/Projects/sdccp/ryu/build/flow_log.txt"
OUTPUT_IMG = "build/multi_flows.png"


def plot_multiflows(f, out, xlim=None, xrange=None):
    with open(f) as fs:
        data = fs.readlines()
    data = [x1.split() for x1 in data]
    start_time = -1

    time_sendingrates = {}
    pre_num = 1
    for line in data:
        if line[1] > '0':
            if start_time == -1:
                start_time = float(line[0])
            num = int(line[1])
            if num > pre_num:
                for k in time_sendingrates.keys():
                    time_sendingrates[k].pop()
                pre_num = num
            time = float(line[0]) - start_time
            if xrange and (time - xrange > 0):
                break
            for i in range(0, num):
                time_sendingrates.setdefault(line[2+i*2], [])
                time_sendingrates[line[2+i*2]].append([float(line[0]) - start_time, float(line[3+i*2]) / 1000000])

    plt.figure()
    for user in time_sendingrates.keys():
        t = [i[0] for i in time_sendingrates[user]]
        s = [i[1] for i in time_sendingrates[user]]
        plt.plot(t, s)
    if xlim:
        plt.xlim(xlim[0], xlim[1])
    plt.xlabel('time (s)')
    plt.ylabel('throughput (Mbps)')
    plt.savefig(out)
    plt.show()


parser = argparse.ArgumentParser()
parser.add_argument('--xlim', '-x',
                    help="xaxis range limit",
                    action="store",
                    dest="xlim")
parser.add_argument('--xrange', '-r',
                    help="xaxis range",
                    action="store",
                    dest="xrange")


if __name__ == '__main__':
    args = parser.parse_args()
    log_file = RYU_LOG_FILE
    output_img = OUTPUT_IMG
    xlim = map(lambda i: int(i), args.xlim.split(',')) if args.xlim else None
    xrange = float(args.xrange) if args.xrange else None
    plot_multiflows(log_file, output_img, xlim=xlim, xrange=xrange)
