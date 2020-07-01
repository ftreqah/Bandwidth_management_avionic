#! /usr/bin/python
# coding: utf-8


import requests
import sys
import time
import matplotlib.pyplot as plt
from datetime import datetime
import simplejson
import os
import json
import argparse
import subprocess
from th_management import getswitchstats


def main():
    if (len(sys.argv)) <= 1:
        print "Type --help for help"
        exit()
    # Call using ./bw_engine -i 10 -t 15000000 -q True -p False
    parser = argparse.ArgumentParser(description="Bandwidth Engine")
    parser.add_argument('-i', '--iter',
                        required=False,
                        default=10,
                        type=int,
                        dest='i',
                        metavar="I")
    parser.add_argument('-t', '--threshold_bits_max',
                        required=False,
                        default=15000000,
                        type=int,
                        dest='t',
                        metavar="T")

    parser.add_argument('-q', '--queuing activate 0:False, 1:True',
                        required=False,
                        default=False,
                        type=bool,
                        dest='q',
                        metavar="Q")

    parser.add_argument('-p', '--police activate 0:False, 1:True',
                        required=False,
                        default=False,
                        type=bool,
                        dest='p',
                        metavar="P")

    args = parser.parse_args()
    # Init arguments
    iteration = args.i
    queuing = args.q
    policing = args.p
    threshold_bits_max = args.t
    # threshold min is 50%
    threshold_bits_min = threshold_bits_max - (50*threshold_bits_max)/100
    c = '127.0.0.1'
    p = '8080'
    mapService = {'Safety': ["10.0.0.1", "10.0.0.2"],
                  'Non-safety': ["10.0.0.3"]}
    host = mapService['Non-safety'][0]
    flow1 = "src=10.0.0.1,dst='10.0.0.4',mark='184',queue=0"
    flow2 = "src=10.0.0.2,dst='10.0.0.4',mark='184',queue=0"
    flow3 = "src=10.0.0.3,dst='10.0.0.5',mark='40',queue=1"

    f = 'th_management.py'
    conf = 'Throughput_Last.json'
    i = 0
    # detect=('False',0)
    print "Starting the bandwith engine for "+str(iteration)+" iterations."
    v_number = 0
    policy_applied = False

    print "Queuing is ", queuing
    print "Q type is ", type(queuing)

    if queuing == 'True':
        print "Queuing activated"
        _queuing()

        src = '10.0.0.1'
        dst = '10.0.0.5'
        mark = 184
        queue = 1
        print "Setup and mark flows"
        _enqueue(src, dst, mark, queue, c, p)

    print "Policing is ", policing
    print "Policing type is ", type(policing)
    # if policing:
    # print "Policing activated"
    try:
        while i < iteration:
            # Run threshold manager
            RunTh(f)
            time.sleep(4)

            if policing == 'True':
                # print "Policing activated"
                # Run violation detection
                detect = Violadetect(
                    host, threshold_bits_max, c, p, conf, v_number)
                print detect
                throughput = detect[3]
                portname = detect[2]
                v_number = detect[1]
                violation_status = detect[0]
                # print "Policy applied ",policy_applied
                if violation_status and v_number >= 2 and not policy_applied:
                    print "###Violation Exceeded "+str(v_number)+", Policing is applied###"
                    burst = (threshold_bits_max -
                             (90*threshold_bits_max)/100)/1000
                    rate = (threshold_bits_max -
                            (10*threshold_bits_max)/100)/1000
                    police(portname, rate, burst, add=True)
                    v_number -= 1
                    policy_applied = True
                # if not (violation_status) and throughput<threshold_bits_min and policy_applied:
                if throughput < threshold_bits_min and policy_applied:
                    print "###No Violation detected, Port releasing is applied###"
                    #burst=threshold_bits_min - (90*threshold_bits_min)/100
                    # Release the port from the policy
                    police(portname, 0, 0, delete=True)
                    policy_applied = False
                    v_number -= 1

                    # time.sleep(3)

            i += 1

    except (KeyboardInterrupt, SystemExit):
        print("Exit")

# Find Output port for policy and mark


def find_output(c, p, src, dst, single=False):
    sw = getswitchstats(c, p)
    d = findDev(c, p)
    l = []
    sw_l = []
    for portname in d:
        pname = portname['port']
        dpid = portname['dpid']
        host = portname['host']
        if host == src:
            switch_src = dpid
        if host == dst:
            switch_dst = dpid
            port_dst = pname
        s = str(dpid)+"."+str(pname)
        l.append(s)

    if switch_dst == switch_src:
        output = port_dst
        single = True
        port_src = 0
        return port_src, port_dst, switch_src, single
    else:
        for dpid, port in sw.items():
            # print dpid
            for i in range(len(port)):
                p = port[i]['port']
                s = str(dpid)+"."+str(p)
                sw_l.append(s)

        for s in sw_l:
            dpid = s.split('.')[0]
            if s not in l and dpid == switch_src:
                port_src = s.split('.')[1]

        return port_src, port_dst, switch_src, switch_dst, single

# Police method
# This is the hard way to limit the traffic coming from the source


def police(portname, rate, burst, add=False, delete=False):
    cmd = 'ovs-vsctl set interface '+str(portname)+' ingress_policing_'
    rate = cmd+'rate='+str(rate)
    burst = cmd+'burst='+str(burst)
    # print rate
    if add:
        try:
            rate_proc = subprocess.Popen(rate, shell=True)
            burst_proc = subprocess.Popen(burst, shell=True)
        except ValueError as e:
            print "Problem run %s" % e
            print e
    if delete:
        try:
            rate_proc = subprocess.Popen(rate, shell=True)
            burst_proc = subprocess.Popen(burst, shell=True)
        except ValueError as e:
            print "Problem run %s" % e
            print e

# Traffic Shape method
# Queuing for all port and all switches availa
# Queue 0: allow 100Mbit/s
# Queue 1: allows 50Mbit/s
# Queue 2: allows 10Mbit/s


def _queuing():
    cmd = "ovs-vsctl list qos"
    p = os.popen(cmd).read()
    if not p:
        cmd = './queues.py -q0 100000000 -q1 50000000 -q2 10000000'
        print "Creating three queues -q0 100000000 -q1 50000000 -q2 10000000"
        try:
            queuecmd = subprocess.Popen(cmd, shell=True)
        except ValueError as e:
            print "Problem run %s" % e
            print e

    return 0
# Enquene and Mark actions


def _enqueue(src, dst, mark, queue, c, p):
    # use the static flow pusher command
    # curl -s -d '{"switch":"00:00:00:00:00:00:00:01","name":"tos-4","ether-type":"0x0800","src-ip":"10.0.0.3","dst-ip":"10.0.0.5","actions":"set-tos-bits=40,enqueue=5:2"}' http://127.0.0.1:8080/wm/staticflowentrypusher/json
    print "Creating new flows for ", src
    findedDevices = findDev(c, p)
    url = " http://%s:%s/wm/staticflowentrypusher/json" % (c, p)
    st = find_output(c, p, src, dst)
    if st[-1]:
        print "Single switch finded, push new flow"
        port = st[0]
        switch = st[1]
        cmd1 = '{"switch":"%s","name":"tos-%s","ether-type":"0x0800","src-ip":"%s","dst-ip":"%s","actions":"set-tos-bits=%s,enqueue=%s:%s"}' % (
            switch, src, src, dst, mark, port, queue)
        cmd1 = "curl -s -d '%s'" % cmd1
        full_cmd1 = cmd1+url
        cmd1_exec = subprocess.Popen(full_cmd1, shell=True)
    if not st[-1]:
        print "Different switches finded, push all corresponding flows"
        port_src = st[0]
        switch_src = st[2]
        port_dst = st[1]
        switch_dst = st[3]
        cmd1 = '{"switch":"%s","name":"tos-%s","ether-type":"0x0800","src-ip":"%s","dst-ip":"%s","actions":"set-tos-bits=%s,enqueue=%s:%s"}' % (
            switch_src, src, src, dst, mark, port_src, queue)
        cmd2 = '{"switch":"%s","name":"tos-%s","ether-type":"0x0800","src-ip":"%s","dst-ip":"%s","actions":"set-tos-bits=%s,enqueue=%s:%s"}' % (
            switch_dst, src, src, dst, mark, port_dst, queue)
        cmd1 = "curl -s -d '%s'" % cmd1
        full_cmd1 = cmd1+url
        cmd1_exec = subprocess.Popen(full_cmd1, shell=True)
        cmd2 = "curl -s -d '%s'" % cmd2
        full_cmd2 = cmd2+url
        cmd2_exec = subprocess.Popen(full_cmd2, shell=True)
    return 0


# Run Th management
def RunTh(f):
    print "Starting threshold calculator"
    try:
        cmd = './'+f+' -i '+str(1)
        net_proc = subprocess.Popen(cmd, shell=True)
        net_proc.wait()
    except ValueError as e:
        print "Problem run %s" % cmd
        print e
    except (KeyboardInterrupt, SystemExit):
        print("Exit")

# Violation detection


def Violadetect(host, threshold, c, p, conf, vnumber):
    findedDevices = findDev(c, p)
    pwd = os.getcwd()
    v_detected = False
    i = 0
    try:
        if os.path.exists("%s/%s" % (pwd, conf)):
            with open(conf) as outfile:
                data = json.load(outfile)
            # Test of Non-safety device policing
            # print findedDevices
            portname = findTh(findedDevices, data, host)[0]
            throughput = findTh(findedDevices, data, host)[1]
            if throughput > threshold:
                vnumber += 1
                v_detected = True
                # Add policy traffic shapping or slow queue reassignemen
            i += 1
        else:
            print conf, " do not exist"

    except (KeyboardInterrupt, SystemExit):
        print("Exit")

    return (v_detected, vnumber, portname, throughput)


# curl -s http://127.0.0.1:8080/wm/device/ | python -mjson.tool
# Get all devices/switches
def findDev(c, p):
    url = "http://%s:%s/wm/device/" % (c, p)
    response1 = requests.get(url)
    devices = response1.json()
    devlist = []
    for device in devices:
        if device['ipv4']:
            host = device['ipv4'][0]
            sw = device['attachmentPoint'][0]['switchDPID']
            port = device['attachmentPoint'][0]['port']
            s = 's'+sw.split(":")[-1][1]
            portname = s+"-eth"+str(port)
            findHost = {'host': host, 'dpid': sw,
                        'port': port, "portname": portname}
            devlist.append(findHost)
    return devlist


def findTh(findedDevices, data, host):
    portname = ''
    throughputrx = 0
    for dp, v in data.items():
        for device in findedDevices:
            if host == device['host'] and dp == device['dpid']:
                for i in range(len(v)):
                    if str(v[i]['name']) == device['portname']:
                        throughputrx = v[i]['Thputbits_rx']
                        portname = v[i]['name']
                        break
                # break
    return (portname, throughputrx)


# Call main :)
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exit")
        # sys.exit(0)
