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
# -*- coding:UTF-8 -*-

# curl http://127.0.0.1:8080/wm/core/controller/switches/json | python -m json.tool
# switches


def main():

    # Variable initialization
    controller = '127.0.0.1'
    PORT = '8080'
    Totalstats = {}
    AllTh = {}
    # iteration=10
    conf = 'refcounter.json'
    conf2 = 'Throughput_Last.json'
    conf3 = 'AllThrouput.json'

    Totalstats = getswitchstats(controller, PORT)
    ThputCalculation(Totalstats, AllTh, conf, conf2, conf3)


def ThputCalculation(Totstats, AllTh, conf, conf2, conf3):
    data2 = {}
    pwd = os.getcwd()

    try:
        if not os.path.exists("%s/%s" % (pwd, conf)):
            print "file %s does not existe in %s " % (conf, pwd)
            print "Writing inside %s in %s " % (conf, pwd)
            with open(conf, 'w') as outfile:
                json.dump(Totstats, outfile, sort_keys=False, indent=3)

        # print "Openning file %s in %s " % (conf,pwd)
        with open(conf) as outfile:
            data2 = json.load(outfile)

    except ValueError as e:
        print "Problem with %s file" % conf
        print e
        exit(1)

    # print json.dumps(data2,sort_keys=True,indent=3)

    if data2 != None:
        print "Calculating the new data rate ..."
        Throughput = comp_dict(data2, Totstats)
        # print json.dumps(Throughput,sort_keys=True,indent=3)
        # Copy new values to refcounters
        with open(conf, 'w') as outfile:
            json.dump(Totstats, outfile, sort_keys=False, indent=3)

    with open(conf2, 'w') as outfile:
        json.dump(Throughput, outfile, sort_keys=False, indent=3)

    # print "Saving all Throughputs ..."
    Newtime = str(time.time()).split('.')[0]
    AllTh[Newtime] = Throughput
    with open(conf3, 'w') as outfile:
        json.dump(AllTh, outfile, sort_keys=True, indent=3)


def getswitchstats(c, p):
    # Getting switches statistics
    url = "http://%s:%s/wm/core/controller/switches/json" % (c, p)
    response1 = requests.get(url)
    switches = response1.json()

    switch_ports = {}
    for switch in switches:
        ports = {}
        dp = switch["dpid"]
        portname = switch['attributes']['DescriptionData']['datapathDescription']
        for port in switch['ports']:
            if port['name'] != portname:
                ports.update({port['name']: port["portNumber"]})
        switch_ports[dp] = ports

    # print switch_ports
    # Getting port statistics
    url2 = "http://%s:%s/wm/core/switch/all/port/json" % (c, p)
    response2 = requests.get(url2)
    portStats = response2.json()

    stats = {}
    ListStats = []
    Totstats = {}

    i = 0
    for sw, p in switch_ports.items():
        ListStats = []
        # print portStats[sw][0]
        while (i < len(portStats[sw])):
            port = portStats[sw][i]['portNumber']
            for n, pp in p.items():
                if pp == port:
                    name = n
                    break
            if port > 0:
                rxBy = portStats[sw][i]['receiveBytes']
                txBy = portStats[sw][i]['transmitBytes']
                t = str(time.time()).split('.')[0]
                stats = {'rxBy': rxBy, 'txBy': txBy,
                         "port": port, "name": name, "time": str(t)}
                ListStats.append(stats)
            i += 1
        i = 0
        Totstats[sw] = ListStats

    return Totstats


def comp_dict(d1, d2):
    NewDict = {}
    for x1, y1 in d1.items():
        NewList = []
        for x2, y2 in d2.items():
            if x1 == x2:
                d2time = str(time.time()).split('.')[0]
                # sw=str(x2)+"."+str(time.time()).split('.')[0]
                ii = 0
                while ii < len(y2):
                    if y1[ii]['name'] == y2[ii]['name']:
                        d1time = y1[ii]['time']
                        name = y2[ii]['name']
                        difftime = int(d2time)-int(d1time)
                        if difftime == 0:
                            difftime = 1
                        Thputbits_rx = (
                            (y2[ii]['rxBy']-y1[ii]['rxBy'])*8)/difftime
                        Thputbits_tx = (
                            (y2[ii]['txBy']-y1[ii]['txBy'])*8)/difftime
                        Thputbits_rx = Thputbits_rx - \
                            (10*int(Thputbits_rx)/100)
                        Thputbits_tx = Thputbits_tx - \
                            (10*int(Thputbits_tx)/100)
                        port = y2[ii]['port']
                        stats = {'Thputbits_rx': Thputbits_rx, 'Thputbits_tx': Thputbits_tx,
                                 "port": port, "name": name, "time": str(datetime.now())}
                        ii += 1
                        # print stats
                        NewList.append(stats)

                NewDict[x2] = NewList
    return NewDict


# Call main :)
if __name__ == "__main__":
    main()
    AllTh = {}
