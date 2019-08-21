#!/usr/bin/python
import argparse
import matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join
from file_process import *
import numpy
import re

log_file_dir = "/home/lam/Projects/sdccp/FCA/build/"
pattern = r'interval:'


def calculate_rtts(f):
    data = open(f).readlines()
    data = [x.split() for x in data]

    rtt = map(lambda d: float(d[4]), data)
    rtt_avg = numpy.average(rtt)
    rtt_std = numpy.std(rtt)
    return rtt_avg, rtt_std


def plot_figure(f, out):
    pass


parser = argparse.ArgumentParser()
parser.add_argument('--expr', '-e',
                    help="Experiment's name",
                    action="store",
                    required=True,
                    dest="expr")


if __name__ == '__main__':
    args = parser.parse_args()
    out = build_dir+'rtt_stats'
    if os.path.exists(out):
        os.remove(out)
    intervals = args.expr.split(',')

    if not os.path.exists(build_dir):
        os.mkdir(build_dir)

    for interval in sorted(intervals, key=lambda x: float(x)):
        log_dir = log_file_dir + interval + '/'
        log_files = [join(log_dir, f) for f in listdir(log_dir) if isfile(join(log_dir, f))]
        output_dir = build_dir + interval + '/'
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        output_file_prefix = output_dir + "formatted_log"
        rtt_avgs = {}
        rtt_stds = {}
        for i, f in enumerate(log_files):
            intermediate_file = output_file_prefix + "_" + str(i)
            format_file(f, intermediate_file)
            rtt_avg, rtt_std = calculate_rtts(intermediate_file)
            rtt_avgs[f.split('/')[-1]] = rtt_avg
            rtt_stds[f.split('/')[-1]] = rtt_std
        log_file_per_interval = output_dir + 'rtt_stats'
        if os.path.exists(log_file_per_interval):
            os.remove(log_file_per_interval)
        open(log_file_per_interval, 'a+')\
            .write("index\trtt_avg\t\trtt_std\n")
        for k in sorted(rtt_stds.keys(), key=lambda x: int(x)):
            open(log_file_per_interval, 'a+')\
                .write("{0}\t\t{1:.3f}\t\t{2:.3f}\n"
                       .format(k, rtt_avgs[k], rtt_stds[k]))
        open(out, 'a+').write('interval: {}, RTT avg.:{}, RTT std.:{}\n'
                              .format(interval, numpy.average(rtt_avgs.values()),
                                      numpy.average(rtt_stds.values())))
