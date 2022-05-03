#!/usr/bin/env python3

import socket
import time
import threading
import os
import datetime as dt
import argparse
import subprocess
import re
import signal
import subprocess

port = 3270


pcap_path = "/home/wmnlab/D/pcap_data2"
now = dt.datetime.today()
n = '-'.join([str(x) for x in[ now.year, now.month, now.day, now.hour, now.minute, now.second]])
pcapfile1 = "%s/UL_%s_%s.pcap"%(pcap_path, port, n)

# socket_proc =  subprocess.Popen(["./server.o %s"%(port)], shell=True)
tcpproc1 =  subprocess.Popen(["tcpdump -i any port %s -w %s &"%(port,  pcapfile1)], shell=True, preexec_fn=os.setsid)

os.system("./server.o %s"%(port))

while True:
    x = input()
    if x == "STOP":
        break

socket_proc =  subprocess.Popen(["killall -p server.o"], shell=True)
os.killpg(os.getpgid(tcpproc1.pid), signal.SIGTERM)
