#!/usr/bin/python
# import argparse
import matplotlib.pyplot as plt

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
    x = map(lambda t: t - start_time, x)
    y = map(lambda s: s / 1000000, y)

    plt.figure()

    plt.plot(x, y)
    plt.xlabel('time(s)')
    plt.ylabel('sending rate (Mbps)')
    plt.show()
    plt.savefig(OUTPUT_FILE)


if __name__ == '__main__':
    main()
