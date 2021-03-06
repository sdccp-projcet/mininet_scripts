#!/usr/bin/python
"""router topology example for TCP competions.
   This remains the default version

router between two subnets:

        h1---80Mbit---r1---bottleneck---r2---80Mbit---h2
                       |
                       |
                       h3

For running a TCP competition, consider the runcompetition.sh script
"""

from mininet.net import Mininet
from mininet.node import Node, OVSKernelSwitch, Controller, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.log import setLogLevel, info
import argparse
import time
import os
import requests


LOG_FILE = '/home/lam/Projects/sdccp/mininet_scripts/build/log.txt'
URL = 'http://localhost:8080/set_bottleneck_capacity_Bps'
DATA = '{{"bottleneck_capacity_Bps": "{}"}}'
AVAILABLE_CC = ['ccp', 'bbr', 'cubic', 'reno']
COMPETE5 = 'compete5'

QUEUE=100
DELAY='50ms'		# r--h3 link
BottleneckBW=50
BBR=False

# reno-bbr parameters:
if BBR:
    DELAY='40ms'
    QUEUE=267
    BottleneckBW=10


parser = argparse.ArgumentParser()
parser.add_argument('--duration', '-d',
                    help="Duration of test in seconds",
                    action="store",
                    dest="duration")
parser.add_argument('--test_option', '-t',
                    help="test type. Current support: %s" % str(COMPETE5),
                    action="store",
                    dest="test_option")
parser.add_argument('--cc', '-c',
                    help="congestion control algorithm to be run",
                    action="store",
                    dest="cc")

# h1addr = '10.0.1.2/24'
# h2addr = '10.0.2.2/24'
# r1addr1= '10.0.1.1/24'
# r1addr2= '10.0.2.1/24'


class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        info ('enabling forwarding on ', self)
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()


class RTopo(Topo):
    #def __init__(self, **kwargs):
    #global r
    def build(self, **_opts):     # special names?
        r1 = self.addSwitch('r1')
        r2 = self.addSwitch('r2')
        h1 = self.addHost('h1', ip='10.0.1.10/24', defaultRoute='via 10.0.1.1')
        h2 = self.addHost('h2', ip='10.0.1.11/24', defaultRoute='via 10.0.1.1')
        h3 = self.addHost('h3', ip='10.0.1.12/24', defaultRoute='via 10.0.1.1')
        h4 = self.addHost('h4', ip='10.0.1.13/24', defaultRoute='via 10.0.1.1')
        h5 = self.addHost('h5', ip='10.0.1.14/24', defaultRoute='via 10.0.1.1')
        # h6 = self.addHost('h6', ip='10.0.1.15/24', defaultRoute='via 10.0.1.1')

        self.addLink( h1, r1, intfName1 = 'h1-eth', intfName2 = 'r1-eth1', bw=80,
                 params2 = {'ip' : '10.0.1.1/24'})

        self.addLink( h2, r1, intfName1 = 'h2-eth', intfName2 = 'r1-eth3', bw=80,
                 params2 = {'ip' : '10.0.1.2/24'})

        self.addLink( h3, r2, intfName1 = 'h3-eth', intfName2 = 'r2-eth1',
                 params2 = {'ip' : '10.0.1.3/24'})

        self.addLink( h4, r1, intfName1 = 'h4-eth', intfName2 = 'r1-eth4', bw=80,
                 params2 = {'ip' : '10.0.1.4/24'})

        self.addLink( h5, r1, intfName1 = 'h5-eth', intfName2 = 'r1-eth5', bw=80,
                 params2 = {'ip' : '10.0.1.5/24'})

        # self.addLink( h6, r1, intfName1 = 'h6-eth', intfName2 = 'r1-eth6', bw=80,
        #          params2 = {'ip' : '10.0.1.6/24'})

        self.addLink(r1, r2, intfName1='r1-eth2', intfName2='r2-eth2',
                     bw=BottleneckBW, delay=DELAY, queue=QUEUE)

# delay is the ONE-WAY delay, and is applied only to traffic departing h3-eth.

# BBW=8: 1 KB/ms, for 1K packets; 110 KB in transit
# BBW=10: 1.25 KB/ms, or 50 KB in transit if the delay is 40 ms.
# queue = 267: extra 400 KB in transit, or 8x bandwidthxdelay


def main(test_option=None, duration=50, cc='bbr'):
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    if test_option and test_option != COMPETE5:
        print("Invalid test_option: " + test_option)
        print("We only support test_option: " + str(COMPETE5))
        return

    if cc not in AVAILABLE_CC:
        print("We only support following cc: " + str(AVAILABLE_CC))
        return

    rtopo = RTopo()
    net = Mininet(topo = rtopo,
                  link=TCLink,
                  #switch = OVSKernelSwitch, 
                  controller = RemoteController,
                  autoSetMacs = True   # --mac
                  )
    net.start()
    data = DATA.format(BottleneckBW * 1000000 / 8)
    print(data)
    requests.put(URL, data=data)

    h1 = net['h1']
    h2 = net['h2']
    h3 = net['h3']
    h4 = net['h4']
    h5 = net['h5']
    # h6 = net['h6']

    h1.cmd('tc qdisc del dev h1-eth root')
    h1.cmd('tc qdisc add dev h1-eth root fq')
    h2.cmd('tc qdisc del dev h2-eth root')
    h2.cmd('tc qdisc add dev h2-eth root fq')
    h3.cmd('tc qdisc del dev h3-eth root')
    h3.cmd('tc qdisc add dev h3-eth root fq')
    h4.cmd('tc qdisc del dev h4-eth root')
    h4.cmd('tc qdisc add dev h4-eth root fq')
    h5.cmd('tc qdisc del dev h5-eth root')
    h5.cmd('tc qdisc add dev h5-eth root fq')
    # h6.cmd('tc qdisc del dev h6-eth root')
    # h6.cmd('tc qdisc add dev h6-eth root fq')

    if test_option:
        if duration <= 10:
            print("Error! Invalid duration: %s. Please input a valid duration for test." % duration)
        time.sleep(1)
        h3.cmd('iperf -s -p 12345 -i 1 &')
        with open(LOG_FILE, 'a+') as f:
            f.write('%s\t%d\n' % (str(time.time()), BottleneckBW))

        if test_option == COMPETE5:
            print("Enable auto test. all clients connect to h2 using %s ..." % cc)
            h1.cmd('iperf -c 10.0.1.12 -p 12345 -i 1 -Z %s -t %d &' % (cc, duration))
            t = 5
            time.sleep(t)
            h2.cmd('iperf -c 10.0.1.12 -p 12345 -i 1 -Z %s -t %d &' % (cc, duration - t))
            time.sleep(t)
            h4.cmd('iperf -c 10.0.1.12 -p 12345 -i 1 -Z %s -t %d &' % (cc, duration - 2 * t))
            time.sleep(t)
            h5.cmd('iperf -c 10.0.1.12 -p 12345 -i 1 -Z %s -t %d &' % (cc, duration - 3 * t))
            time.sleep(t)
            # h6.cmd('iperf -c 10.0.1.12 -p 12345 -i 1 -Z %s -t %d &' % (cc, duration - 4 * t))
            time.sleep(duration + 10 - 4 * t)
        net.stop()
        return

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    args = parser.parse_args()
    duration = args.duration if args.duration else 50
    cc = args.cc if args.cc else 'bbr'
    test_option = args.test_option if args.test_option else None
    main(test_option=test_option, duration=int(duration), cc=cc)


"""
This leads to a queuing hierarchy on r with an htb node, 5:0, as the root qdisc. 
The class below it is 5:1. Below that is a netem qdisc with handle 10:, with delay 110.0ms.
We can change the limit (maximum queue capacity) with:

    tc qdisc change dev r-eth1 handle 10: netem limit 5 delay 110.0ms

"""
