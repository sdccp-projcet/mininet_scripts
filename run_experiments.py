#!/usr/bin/python
import argparse
import subprocess
import os
from time import sleep
from multiprocessing import Process, Queue, cpu_count


parser = argparse.ArgumentParser()
parser.add_argument('--number', '-n',
                    help="The number of experiments to run",
                    action="store",
                    required=True,
                    dest="number")

DURATION = "10"
FCA_PATH = "/home/lam/Projects/sdccp/FCA/"
FCA_CMD = "sudo ./target/debug/reno --ipc netlink --init_cwnd 1600 &"
MININET_PATH = "/home/lam/Projects/sdccp/mininet_scripts/"
MININET_CMD = "sudo ./competition.py -s ccp -d {}".format(DURATION)
LOG_FILE = FCA_PATH + "log_output1.txt"
OUTPUT_PATH = FCA_PATH + "build/1/"


def run_FCA():
    os.chdir(FCA_PATH)
    subprocess.call(FCA_CMD, shell=True)
    sleep(int(DURATION) + 10)
    print("fca")


def run_mininet():
    os.chdir(MININET_PATH)
    subprocess.call(MININET_CMD, shell=True)
    sleep(int(DURATION) + 10)
    print("mininet")


def mv_file(i):
    os.chdir(FCA_PATH)
    # subprocess.call("mv {} {}".format(LOG_FILE, OUTPUT_PATH + str(i)))
    subprocess.call("ls")
    subprocess.call("sudo cp log_output1.txt build/1/1", shell=True)


def main():
    print("The number of CPU is:" + str(cpu_count()))
    args = parser.parse_args()
    for i in range(int(args.number)):
        p1 = Process(target=run_FCA)
        p2 = Process(target=run_mininet)
        p1.start()
        sleep(1)
        p2.start()
        p2.join()
        p1.terminate()
        sleep(2)
        mv_file(i)


if __name__ == '__main__':
    main()
