#! /usr/bin/python
#  coding: utf-8

'''
Add queues to Mininet using ovs-vsctl and ovs-ofctl
@Author Ryan Wallner
'''

import os
import sys
import time
import subprocess
import argparse


def main():
    if (len(sys.argv)) <= 1:
        print "Type --help for help"
        exit()
    parser = argparse.ArgumentParser(description="Queue setup")
    parser.add_argument('-q0', '--q0 ex fast 100Mb:100000000',
                        required=False,
                        default=10,
                        type=int,
                        dest='q0',
                        metavar="Q0")
    parser.add_argument('-q1', '--q1 ex medium 50Mb:50000000',
                        required=False,
                        default=10,
                        type=int,
                        dest='q1',
                        metavar="Q1")
    parser.add_argument('-q2', '--q2 ex slow 10Mb:10000000',
                        required=False,
                        default=10,
                        type=int,
                        dest='q2',
                        metavar="Q2")

    args = parser.parse_args()
    # Init arguments
    q0 = str(args.q0)
    q1 = str(args.q1)
    q2 = str(args.q2)
    print type(q0), q0

    apply_qos(q0, q1, q2)


def find_all(a_str, sub_str):
    start = 0
    b_starts = []
    while True:
        start = a_str.find(sub_str, start)
        if start == -1:
            return b_starts
        # print start
        b_starts.append(start)
        start += 1


def apply_qos(q0, q1, q2):
    if os.getuid() != 0:
        print "Root permissions required"
        exit()

    cmd = "ovs-vsctl show"
    p = os.popen(cmd).read()
    # print p

    brdgs = find_all(p, "Bridge")
    print brdgs

    switches = []
    for bn in brdgs:
        sw = p[(bn+8):(bn+10)]
        switches.append(sw)

    ports = find_all(p, "Port")
    print ports

    prts = []
    for prt in ports:
        prt = p[(prt+6):(prt+13)]
        if '"' not in prt:
            print prt
            prts.append(prt)
    config_strings = {}
    for i in range(len(switches)):
        str = ""
        sw = switches[i]
        for n in range(len(prts)):
            # verify correct order
            if switches[i] in prts[n]:
                # print switches[i]
                # print prts[n]
                port_name = prts[n]
                str = str+" -- set port %s qos=@defaultqos" % port_name
        config_strings[sw] = str

    cmd = "id=@defaultqos create qos type=linux-htb other-config:max-rate="+q0+" queues=0=@q0,1=@q1,2=@q2 -- --id=@q0 create queue other-config:min-rate="+q0 + \
        " other-config:max-rate="+q0+" -- --id=@q1 create queue other-config:max-rate="+q1 + \
        " -- --id=@q2 create queue other-config:max-rate="+q2+" other-config:min-rate="+q2

    # build queues per sw
    print config_strings
    for sw in switches:
        queuecmd = "sudo ovs-vsctl %s -- --" % config_strings[sw]
        queuecmd_final = queuecmd+cmd
        q_res = os.popen(queuecmd_final).read()
        print q_res


# Call main :)
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exit")
        # sys.exit(0)
