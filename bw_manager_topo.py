#!/usr/bin/python

"""
This example shows a Mininet topology simulating avionic cookpit network.
"""

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import os


def bw_engine():
    "Create an empty network and add nodes to it."

    net = Mininet(controller=None, switch=OVSKernelSwitch)

    info('*** Adding controller\n')
    net.addController('c0', controller=RemoteController,
                      ip='127.0.0.1', port=6633)

    info('*** Adding hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    h3 = net.addHost('h3', ip='10.0.0.3')
    h4 = net.addHost('h4', ip='10.0.0.4')
    h5 = net.addHost('h5', ip='10.0.0.5')

    info('*** Adding switch\n')
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')

    info('*** Creating links\n')
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s2)
    net.addLink(s1, s3)
    net.addLink(s2, s3)
    net.addLink(s3, h4)
    net.addLink(s3, h5)

    info('*** Starting network\n')
    net.start()
    net.pingAll()
    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network')
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    print "Clear old statistics"
    cmd = "./clear_switchports.py"
    os.popen(cmd).read()
    bw_engine()
