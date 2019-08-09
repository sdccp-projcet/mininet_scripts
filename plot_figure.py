#!/usr/bin/python
import argparse
import re
import os
import matplotlib.pyplot as plt

pattern = re.compile(
    r'tv_sec:\s([\d]+),\stv_nsec:\s(\d*)\s}\slink_utilization:\s(\d.\d+)\s'
    r'queue:\s(-?\d+)\scwnd:\s(\d+)\srtt:\s(\d+.\d+)'
)

build_dir = "build/"
log_file = "/home/lam/Projects/sdccp/remote-generic/log_output"
output_file = build_dir + "formatted_log"


def format_file(file_in, file_out):
    f_in = open(file_in, "r")
    if not os.path.exists(build_dir):
        os.mkdir(build_dir)
    if os.path.exists(file_out):
        os.remove(file_out)
    for x in f_in:
        matches = pattern.findall(x)
        i = 1
        for m in matches:
            for k in m:
                if i == 1:
                    open(file_out, 'a').write(str(k) + '.')
                    i += 1
                elif i == 2:
                    open(file_out, 'a').write(str(k).zfill(9) + '\t')
                    i += 1
                else:
                    open(file_out, 'a').write(str(k) + '\t')
            open(file_out, 'a').write('\n')


def plot_figure(f, out):
    data = open(f).readlines()
    data = [x.split() for x in data]
    times = map(lambda d: float(d[0]), data)
    start_time = times[0]
    times = [t - start_time for t in times]
    plt.figure()

    plt.subplot(411)
    link_utilizations = map(lambda d: float(d[1]), data)
    plt.plot(times, link_utilizations)
    plt.xlabel('time')
    plt.ylabel('link_utilization')

    plt.subplot(412)
    queues = map(lambda d: float(d[2]), data)
    plt.plot(times, queues)
    plt.xlabel('time')
    plt.ylabel('queues')

    plt.subplot(413)
    cwnds = map(lambda d: float(d[3]), data)
    plt.plot(times, cwnds)
    plt.xlabel('time')
    plt.ylabel('cwnd')

    plt.subplot(414)
    rtt = map(lambda d: float(d[4]), data)
    plt.plot(times, rtt)
    plt.xlabel('time')
    plt.ylabel('rtt')

    plt.savefig(out)
    plt.show()


parser = argparse.ArgumentParser()
parser.add_argument('--expr', '-e',
                    help="Experiment's name",
                    action="store",
                    dest="expr")


if __name__ == '__main__':
    args = parser.parse_args()
    if args.expr:
        log_file += args.expr
        output_file += args.expr
    log_file += ".txt"
    output_img = output_file
    output_file += ".txt"
    format_file(log_file, output_file)
    plot_figure(output_file, output_img)
