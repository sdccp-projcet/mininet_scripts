#!/usr/bin/python
# import argparse
import matplotlib.pyplot as plt
from competition import LOG_FILE as SCRIPT_FILE

# parser = argparse.ArgumentParser()
# parser.add_argument('--expr', '-e',
#                     help="Experiment's name",
#                     action="store",
#                     required=True,
#                     dest="expr")

LOG_FILE = '/home/lam/Projects/sdccp/ryu/build/log.txt'
OUTPUT_FILE = 'build/bandwidth.png'


def main():
    data = open(LOG_FILE).readlines()
    data = [d.split() for d in data]
    data = filter(lambda x: x[1][0] != '0', data)
    data = map(lambda x: [float(k) for k in x], data)
    start_time = data[0][0]
    x = [d[0] for d in data]
    y = [d[1] for d in data]
    q = [d[2] for d in data]
    l = [d[3] for d in data]
    x = map(lambda t: t - start_time, x)
    y = map(lambda s: s / 1000000, y)
    q = map(lambda s: s / 1000, q)

    data = open(SCRIPT_FILE).readlines()
    data = [d.split() for d in data]
    data = map(lambda x: [float(k) for k in x], data)
    x1 = [d[0] for d in data]
    y1 = [d[1] for d in data]
    x1 = map(lambda t: t - start_time, x1)

    plt.figure()
    ax1 = plt.subplot(211)

    color = 'tab:red'
    ax1.set_xlabel('time(s)')
    ax1.set_ylabel('sending rate (Mbps)')
    ax1.plot(x, y, 'b', x1, y1, 'r')
    ax1.tick_params(axis='y', labelcolor=color)

    # plt.plot(x, y, 'b', x1, y1, 'r')
    # plt.xlabel('time(s)')
    # plt.ylabel('sending rate (Mbps)')
    ax2 = ax1.twinx()

    color = 'tab:green'
    ax2.set_ylabel('link utilization', color=color)
    ax2.plot(x, l, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    plt.subplot(212)
    plt.plot(x, q, 'b')
    plt.xlabel('time (s)')
    plt.ylabel('queue size (kb)')

    plt.savefig(OUTPUT_FILE)
    plt.show()


if __name__ == '__main__':
    main()
