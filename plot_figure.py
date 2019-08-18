#!/usr/bin/python
import argparse
import matplotlib.pyplot as plt
from file_process import *

log_file = "/home/lam/Projects/sdccp/FCA/log_output"
output_file = build_dir + "formatted_log"


def plot_figure(f, out, xlim=None):
    data = open(f).readlines()
    data = [x.split() for x in data]
    times = map(lambda d: float(d[0]), data)
    start_time = times[0]
    times = [t - start_time for t in times]
    plt.figure()

    plt.subplot(411)
    link_utilizations = map(lambda d: float(d[1]), data)
    if xlim:
        plt.xlim(0, xlim)
    plt.ylim(0, 1.2)
    plt.plot(times, link_utilizations)
    plt.xlabel('time')
    plt.ylabel('link_utilization')

    plt.subplot(412)
    queues = map(lambda d: float(d[2]), data)
    if xlim:
        plt.xlim(0, xlim)
    plt.ylim(0, 100)
    plt.plot(times, queues)
    plt.xlabel('time')
    plt.ylabel('queues (packets)')

    plt.subplot(413)
    cwnds = map(lambda d: float(d[3]), data)
    if xlim:
        plt.xlim(0, xlim)
    plt.ylim(0, 100)
    plt.plot(times, cwnds)
    plt.xlabel('time')
    plt.ylabel('cwnd (packets)')

    plt.subplot(414)
    rtt = map(lambda d: float(d[4]), data)
    if xlim:
        plt.xlim(0, xlim)
    # plt.yscale("log")
    plt.ylim(100, 400)
    plt.plot(times, rtt)
    plt.xlabel('time (s)')
    plt.ylabel('rtt (ms)')

    plt.savefig(out)
    plt.show()


parser = argparse.ArgumentParser()
parser.add_argument('--expr', '-e',
                    help="Experiment's name",
                    action="store",
                    dest="expr")
parser.add_argument('--xlim', '-x',
                    help="xaxis range limit",
                    action="store",
                    dest="xlim")


if __name__ == '__main__':
    args = parser.parse_args()
    if args.expr:
        log_file += args.expr
        output_file += args.expr
    log_file += ".txt"
    output_img = output_file
    output_file += ".txt"
    format_file(log_file, output_file)
    if args.xlim:
        plot_figure(output_file, output_img, xlim=int(args.xlim))
    else:
        plot_figure(output_file, output_img)
