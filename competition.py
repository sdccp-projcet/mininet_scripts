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
parser.add_argument('--autotest', '-a',
                    help="The cc algorithm to run in auto test",
                    action="store",
                    dest="autotest")
parser.add_argument('--duration', '-d',
                    help="Duration of test",
                    action="store",
                    dest="duration")
parser.add_argument('--simpletest', '-s',
                    help="The cc algorithm to run in auto test",
                    action="store",
                    dest="simpletest")

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

        self.addLink( h3, r1, intfName1 = 'h3-eth', intfName2 = 'r1-eth3', bw=80,
                 params2 = {'ip' : '10.0.1.3/24'})

        self.addLink( h2, r2, intfName1 = 'h2-eth', intfName2 = 'r2-eth1',
                 params2 = {'ip' : '10.0.1.2/24'})

        self.addLink(r1, r2, intfName1='r1-eth2', intfName2='r2-eth2',
                     bw=BottleneckBW, delay=DELAY, queue=QUEUE)

# delay is the ONE-WAY delay, and is applied only to traffic departing h3-eth.

# BBW=8: 1 KB/ms, for 1K packets; 110 KB in transit
# BBW=10: 1.25 KB/ms, or 50 KB in transit if the delay is 40 ms.
# queue = 267: extra 400 KB in transit, or 8x bandwidthxdelay


def main(is_auto_test=None, duration=10, simple_test=None):
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

    if is_auto_test or simple_test:
        test_type = is_auto_test if is_auto_test else simple_test
        if duration <= 0:
            print("Error! Invalid duration: %s. Please input a valid duration for test." % duration)
        print("Enable auto test. h1 connect to h2 using %s ..." % test_type)
        time.sleep(1)
        h2.cmd('iperf -s -p 12345 -i 1 &')
        h1.cmd('iperf -c 10.0.1.11 -p 12345 -i 1 -Z %s -t %d &' % (test_type, duration))
        if is_auto_test:
            time.sleep(0.2)
            h3.cmd('iperf -c 10.0.1.11 -p 12345 -i 1 -Z %s -t %d &' % (test_type, duration))
        time.sleep(duration * 1.5)
        net.stop()
        return

    CLI( net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    args = parser.parse_args()
    if args.autotest:
        if args.duration:
            main(is_auto_test=args.autotest, duration=int(args.duration))
        else:
            main(is_auto_test=args.autotest)
    elif args.simpletest:
        if args.duration:
            main(simple_test=args.simpletest, duration=int(args.duration))
        else:
            main(simple_test=args.simpletest)
    else:
        main()



"""
This leads to a queuing hierarchy on r with an htb node, 5:0, as the root qdisc. 
The class below it is 5:1. Below that is a netem qdisc with handle 10:, with delay 110.0ms.
We can change the limit (maximum queue capacity) with:

	tc qdisc change dev r-eth1 handle 10: netem limit 5 delay 110.0ms

"""
