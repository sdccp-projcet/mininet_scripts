#!/usr/bin/python
import argparse
import re
import os
import matplotlib.pyplot as plt

pattern = re.compile(
    r'(\d+.\d+),(\d+k?)'
)

build_dir = "build/"
log_file = "/home/lam/Projects/sdccp/mininet_scripts/cubic_sw0-qlen"
output_file = build_dir + "formatted_log"

f1 = "/home/lam/Projects/sdccp/mininet_scripts/cubic_sw0-qlen.txt"
f2 = "/home/lam/Projects/sdccp/mininet_scripts/build/formatted_log1.txt"
out = build_dir + "compare.png"


def format_file(file_in, file_out):
    f_in = open(file_in, "r")
    if not os.path.exists(build_dir):
        os.mkdir(build_dir)
    if os.path.exists(file_out):
        os.remove(file_out)
    for x in f_in:
        matches = pattern.findall(x)
        for m in matches:
            for k in m:
                open(file_out, 'a').write(str(k) + '\t')
            open(file_out, 'a').write('\n')


def plot_figure(f, out):
    data = open(f).readlines()
    data = [x.split() for x in data]
    times = map(lambda d: float(d[0]), data)
    start_time = times[0]
    times = [t - start_time for t in times]
    plt.figure()

    queues = map(lambda d: float(d[1])/1480, data)
    # plt.ylim(0, 100)
    plt.xlim(0, 100)
    plt.plot(times, queues)
    plt.xlabel('time')
    plt.ylabel('queues')
    plt.show()


def plot_compare(f1, f2, out):
    data = open(f1).readlines()
    data = [x1.split(',') for x1 in data]
    x1 = map(lambda d: float(d[0]), data)
    start_time = x1[0]
    x1 = [t - start_time for t in x1]
    y1 = map(lambda d: float(d[1])/1480, data)

    data = open(f2).readlines()
    data = [x.split() for x in data]
    x2 = map(lambda d: float(d[0]), data)
    start_time = x2[0]
    x2 = [t - start_time for t in x2]
    y2 = map(lambda d: float(d[2]), data)
    plt.figure()

    # plt.subplot(211)
    # plt.xlim(0, 100)
    # plt.plot(x1, y1)
    # plt.subplot(212)
    # plt.xlim(0, 100)
    # plt.plot(x2, y2)

    plt.xlim(0, 100)
    plt.xlabel('time (s)')
    plt.ylabel('queue length (packets)')
    plt.plot(x1, y1, label='cubic')
    plt.plot(x2, y2, label='ccp')
    plt.legend()
    # plt.plot(x1, y1, 'b', x2, y2, 'r')

    plt.savefig(out)
    plt.show()


parser = argparse.ArgumentParser()
parser.add_argument('--expr', '-e',
                    help="Experiment's name",
                    action="store",
                    dest="expr")
parser.add_argument('--cmp', '-c',
                    help="Draw comparison of two CCs",
                    action="store_true",
                    dest="cmp",
                    default=False)


if __name__ == '__main__':
    """
    Note that this file does not process data in advance. 
    It requires the user to format the log at first, e.g., by run plot_figure.py.
    """
    args = parser.parse_args()
    if args.cmp:
        plot_compare(f1, f2, out)
    else:
        if args.expr:
            log_file += args.expr
            output_file += args.expr
        log_file += ".txt"
        output_img = output_file
        output_file += ".txt"
        format_file(log_file, output_file)
        plot_figure(output_file, output_img)
