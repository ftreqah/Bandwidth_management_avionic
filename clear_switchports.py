#! /usr/bin/python
#  coding: utf-8

import os
import sys
import time
import subprocess

conf = 'Throughput_Last.json'
conf2 = 'refcounter.json'
conf3 = 'AllThrouput.json'


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


cmd = "ovs-vsctl show"
p = os.popen(cmd).read()
ports = find_all(p, "Port")
# print ports
prts = []
for prt in ports:
    prt = p[(prt+6):(prt+13)]
    if '"' not in prt:
        prts.append(prt)
for n in range(len(prts)):
    port_name = prts[n]
    # print port_name
    # print n
    rate = 'ovs-vsctl set interface '+str(port_name)+' ingress_policing_rate=0'
    burst = 'ovs-vsctl set interface ' + \
        str(port_name)+' ingress_policing_burst=0'
    rate_proc = subprocess.Popen(rate, shell=True)
    burst_proc = subprocess.Popen(burst, shell=True)

# Remove Qos policy
cmd = "ovs-vsctl list qos"
p = os.popen(cmd).read()
clearcmd = "ovs-vsctl -- --all destroy Qos -- --all destroy Queue"
if p:
    os.popen(clearcmd)


# Remove old statistis and policies
print "Clearing Old Statistics and Policies"
pwd = os.getcwd()
try:
    if os.path.exists("%s/%s" % (pwd, conf)):
        os.remove(conf)
    if os.path.exists("%s/%s" % (pwd, conf2)):
        os.remove(conf2)
    if os.path.exists("%s/%s" % (pwd, conf3)):
        os.remove(conf3)
except ValueError as e:
    print "Problem with file %s,%s,%s" % (conf, conf2, conf3)
    print e
    exit(1)
