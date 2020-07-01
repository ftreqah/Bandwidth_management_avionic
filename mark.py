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

'''
Topology 1: H1,H2 --S1 --S3--H4,H5
			|
		H3--S2--

Topology 2: H1,H2,H3 --S1 --H4,H5
'''


def main():
    if (len(sys.argv)) <= 1:
        print "Type --help for help"
        exit()
    parser = argparse.ArgumentParser(description="Mark")
    parser.add_argument('-t', '--topo 1 (multi), 2(single)',
                        required=False,
                        default=1,
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
    topo = str(args.t)
    q = args.q
    p = args.p
    print q
    print p
    #cmd="ovs-vsctl list qos"
    #output = subprocess.check_output(cmd, shell=False)
    #cmd = "ovs-vsctl list qos"
    #p = os.popen(cmd).read()
    #clearcmd="ovs-vsctl -- --all destroy Qos -- --all destroy Queue"
    # if p:
    # c=os.popen(clearcmd)
    # if not p:
    # print "No Qos available"
    # print output
    '''
    #if topo=='1':
#	cmd1= "ovs-ofctl add-flow s1 'ip,nw_src=10.0.0.1,actions=mod_nw_tos:184,output=3'"
#	cmd2= "ovs-ofctl add-flow s1 'ip,nw_src=10.0.0.2,actions=mod_nw_tos:136,output=3'"
#	cmd3= "ovs-ofctl add-flow s2 'ip,nw_src=10.0.0.3,actions=mod_nw_tos:40,output=2'"
 #   if topo=='2':
#	cmd1= "ovs-ofctl add-flow s1 'ip,nw_src=10.0.0.1,actions=mod_nw_tos:184,output=4'"
#	cmd2= "ovs-ofctl add-flow s1 'ip,nw_src=10.0.0.2,actions=mod_nw_tos:136,output=4'"
#	cmd3= "ovs-ofctl add-flow s1 'ip,nw_src=10.0.0.3,actions=mod_nw_tos:40,output=5'"
 #   try:
#	    flow1_proc = subprocess.Popen(cmd1, shell=True)
 #   	    flow2_proc = subprocess.Popen(cmd2, shell=True)
  #          flow3_proc = subprocess.Popen(cmd3, shell=True)
   # except ValueError as e:
    #    print "Problem with file %s,%s,%s" % (f1,f2,f3)
     #   print e
      #  exit(1)
    '''
# Call main :)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exit")
        # sys.exit(0)
