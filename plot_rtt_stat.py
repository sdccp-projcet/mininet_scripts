#!/usr/bin/python
import argparse
import matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join
from file_process import *
import numpy

log_file_dir = "/home/lam/Projects/sdccp/FCA/build/"
output_file = build_dir + "formatted_log"


def plot_figure(f, out):
    if os.path.exists(out):
        os.remove(out)
    data = open(f).readlines()
    data = [x.split() for x in data]

    rtt = map(lambda d: float(d[4]), data)
    rtt_avg = numpy.average(rtt)
    rtt_std = numpy.std(rtt)
    open(out, 'a').write('RTT avg.:{}, RTT std.:{}'.format(rtt_avg, rtt_std))


parser = argparse.ArgumentParser()
parser.add_argument('--expr', '-e',
                    help="Experiment's name",
                    action="store",
                    required=True,
                    dest="expr")


if __name__ == '__main__':
    args = parser.parse_args()
    if args.expr:
        log_file_dir += args.expr + '/'
        output_file += args.expr
    log_files = [f for f in listdir(log_file_dir) if isfile(join(log_file_dir, f))]
    log_files = map(lambda x: log_file_dir+x, log_files)
    for i, f in enumerate(log_files):
        intermediate_file = output_file + str(i)
        format_file(f, intermediate_file)
        plot_figure(intermediate_file, build_dir+'rtt_stats'+'_'+args.expr)
