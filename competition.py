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


TEST_OPTIONS = ['single', 'compete', 'heterogeneous', 'dynamic']
AVAILABLE_CC = ['ccp', 'bbr', 'cubic', 'reno']

QUEUE=100
DELAY='110ms'		# r--h3 link
BottleneckBW=4
BBR=False

# reno-bbr parameters:
if BBR:
    DELAY='40ms'	
    QUEUE=267
    # QUEUE=25
    QUEUE=10
    BottleneckBW=10


parser = argparse.ArgumentParser()
parser.add_argument('--duration', '-d',
                    help="Duration of test in seconds",
                    action="store",
                    dest="duration")
parser.add_argument('--test_option', '-t',
                    help="test type. Current support: %s" % str(TEST_OPTIONS),
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
        defaultIP1 = '10.0.1.1/24'  # IP address for r0-eth1
        defaultIP2 = '10.0.1.2/24'  # IP address for r0-eth1
        # r1 = self.addNode( 'r1', cls=LinuxRouter, ip=defaultIP1 )
        # r2 = self.addNode( 'r2', cls=LinuxRouter, ip=defaultIP2 )
        r1 = self.addSwitch('r1')
        r2 = self.addSwitch('r2')
        h1 = self.addHost( 'h1', ip='10.0.1.10/24', defaultRoute='via 10.0.1.1' )
        h2 = self.addHost( 'h2', ip='10.0.1.11/24', defaultRoute='via 10.0.1.1' )
        h3 = self.addHost( 'h3', ip='10.0.1.12/24', defaultRoute='via 10.0.1.1' )
        #  h1---80Mbit---r1---8Mbit/100ms---r2---80Mbit---h2
 
        self.addLink( h1, r1, intfName1 = 'h1-eth', intfName2 = 'r1-eth1', bw=80,
                 params2 = {'ip' : '10.0.1.1/24'})

        self.addLink( h2, r1, intfName1 = 'h2-eth', intfName2 = 'r1-eth3', bw=80,
                 params2 = {'ip' : '10.0.1.2/24'})

        self.addLink( h3, r2, intfName1 = 'h3-eth', intfName2 = 'r2-eth1',
                 params2 = {'ip' : '10.0.1.3/24'})

        self.addLink(r1, r2, intfName1='r1-eth2', intfName2='r2-eth2',
                     bw=BottleneckBW, delay=DELAY, queue=QUEUE)

# delay is the ONE-WAY delay, and is applied only to traffic departing h3-eth.

# BBW=8: 1 KB/ms, for 1K packets; 110 KB in transit
# BBW=10: 1.25 KB/ms, or 50 KB in transit if the delay is 40 ms.
# queue = 267: extra 400 KB in transit, or 8x bandwidthxdelay


def main(test_option=None, duration=10, cc='bbr'):
    if test_option:
        if test_option not in TEST_OPTIONS:
            print("We only support following test_options: " + str(TEST_OPTIONS))
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
    r1 = net['r1']
    r2 = net['r2']
    # r.cmd('ip route list')
    # r1.cmd('ifconfig r1-eth1 10.0.1.1/24')
    # r2.cmd('ifconfig r2-eth1 10.0.1.2/24')
    # r1.cmd('sysctl net.ipv4.ip_forward=1')
    # r2.cmd('sysctl net.ipv4.ip_forward=1')
    r1.cmd('tc qdisc change dev r1-eth2 handle 10: netem limit {}'.format(QUEUE))

    h1 = net['h1']
    h2 = net['h2']
    h3 = net['h3']

    h1.cmd('tc qdisc del dev h1-eth root')
    h1.cmd('tc qdisc add dev h1-eth root fq')
    h2.cmd('tc qdisc del dev h2-eth root')
    h2.cmd('tc qdisc add dev h2-eth root fq')
    h3.cmd('tc qdisc del dev h3-eth root')
    h3.cmd('tc qdisc add dev h3-eth root fq')

    if test_option:
        if duration <= 0:
            print("Error! Invalid duration: %s. Please input a valid duration for test." % duration)
        print("Enable auto test. h1 connect to h2 using %s ..." % cc)
        time.sleep(1)
        h3.cmd('iperf -s -p 12345 -i 1 &')

        if test_option == 'single':
            h1.cmd('iperf -c 10.0.1.12 -p 12345 -i 1 -Z %s -t %d &' % (cc, duration))
            time.sleep(duration + 10)
        elif test_option == 'compete':
            h1.cmd('iperf -c 10.0.1.12 -p 12345 -i 1 -Z %s -t %d &' % (cc, duration))
            time.sleep(duration/2)
            h2.cmd('iperf -c 10.0.1.12 -p 12345 -i 1 -Z %s -t %d &' % (cc, duration/2))
            time.sleep(duration/2 + 10)
        elif test_option == 'heterogeneous':
            h1.cmd('iperf -c 10.0.1.12 -p 12345 -i 1 -Z ccp -t %d &' % duration)
            time.sleep(1)
            h2.cmd('iperf -c 10.0.1.12 -p 12345 -i 1 -Z cubic -t %d &' % duration)
            time.sleep(duration + 10)
        elif test_option == 'dynamic':
            h1.cmd('iperf -c 10.0.1.12 -p 12345 -i 1 -Z %s -t %d &' % (cc, duration))
            time.sleep(duration / 3)
            r1.cmd('tc class change dev r1-eth2 parent 5:0 classid 5:1 htb rate 2Mbit')
            time.sleep(duration / 3)
            r1.cmd('tc class change dev r1-eth2 parent 5:0 classid 5:1 htb rate 4Mbit')
            time.sleep(duration / 3 + 10)
        net.stop()
        return

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    args = parser.parse_args()
    duration = args.duration if args.duration else 10
    cc = args.cc if args.cc else 'bbr'
    test_option = args.test_option if args.test_option else None
    main(test_option=test_option, duration=int(duration), cc=cc)


"""
This leads to a queuing hierarchy on r with an htb node, 5:0, as the root qdisc. 
The class below it is 5:1. Below that is a netem qdisc with handle 10:, with delay 110.0ms.
We can change the limit (maximum queue capacity) with:

    tc qdisc change dev r-eth1 handle 10: netem limit 5 delay 110.0ms

"""
