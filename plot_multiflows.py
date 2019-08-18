#!/usr/bin/python
import argparse
import re
import os
import matplotlib.pyplot as plt
from file_process import *

log_file = "/home/lam/Projects/sdccp/FCA/log_output"
output_file = build_dir + "formatted_log"
output_img = build_dir + "compare"


def plot_multiflows(f1, f2, out, xlim=None):
    data1 = open(f1).readlines()
    data1 = [x1.split() for x1 in data1]
    time1 = map(lambda d: float(d[0]), data1)
    start_time = time1[0]
    time1 = [t - start_time for t in time1]

    data2 = open(f2).readlines()
    data2 = [x2.split() for x2 in data2]
    time2 = map(lambda d: float(d[0]), data2)
    time2 = [t - start_time for t in time2]
    plt.figure()

    plt.subplot(411)
    link_utilizations1 = map(lambda d: float(d[1]), data1)
    link_utilizations2 = map(lambda d: float(d[1]), data2)
    if xlim:
        plt.xlim(0, xlim)
    plt.ylim(0, 1.2)
    plt.plot(time1, link_utilizations1,
             time2, link_utilizations2)
    plt.xlabel('time')
    plt.ylabel('link_utilization')

    plt.subplot(412)
    rtt1 = map(lambda d: float(d[4]), data1)
    rtt2 = map(lambda d: float(d[4]), data2)
    if xlim:
        plt.xlim(0, xlim)
    # plt.yscale("log")
    plt.ylim(100, 400)
    plt.plot(time1, rtt1,
             time2, rtt2)
    plt.xlabel('time (s)')
    plt.ylabel('rtt (ms)')

    plt.subplot(413)
    cwnds_1 = map(lambda d: float(d[3]), data1)
    cwnds_2 = map(lambda d: float(d[3]), data2)
    if xlim:
        plt.xlim(0, xlim)
    plt.ylim(0, 100)
    plt.plot(time1, cwnds_1,
             time2, cwnds_2)
    plt.xlabel('time')
    plt.ylabel('cwnd (packets)')

    plt.subplot(414)
    queues = map(lambda d: float(d[2]), data1)
    if xlim:
        plt.xlim(0, xlim)
    plt.ylim(0, 100)
    plt.plot(time1, queues)
    plt.xlabel('time')
    plt.ylabel('queues (packets)')

    plt.savefig(out)
    plt.show()


parser = argparse.ArgumentParser()
parser.add_argument('--expr1', '-e',
                    help="Experiment1's name",
                    action="store",
                    required=True,
                    dest="expr1")
parser.add_argument('--expr2', '-f',
                    help="Experiment2's name",
                    action="store",
                    required=True,
                    dest="expr2")

parser.add_argument('--xlim', '-x',
                    help="xaxis range limit",
                    action="store",
                    dest="xlim")


if __name__ == '__main__':
    args = parser.parse_args()
    log_file1 = log_file + args.expr1 + ".txt"
    log_file2 = log_file + args.expr2 + ".txt"
    output_file1 = output_file + args.expr1 + ".txt"
    output_file2 = output_file + args.expr2 + ".txt"
    output_img += "_" + args.expr1 + "_" + args.expr2
    format_file(log_file1, output_file1)
    format_file(log_file2, output_file2)
    if args.xlim:
        plot_multiflows(output_file1, output_file2, output_img, xlim=int(args.xlim))
    else:
        plot_multiflows(output_file1, output_file2, output_img)
