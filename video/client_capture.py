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


pcap_path = "/home/wmnlab/data"
PORT = 1935
hostname = str(PORT) + ":"

now = dt.datetime.today()
n = '-'.join([str(x) for x in[ now.year, now.month, now.day, now.hour, now.minute, now.second]])
pcapfile1 = "%s/client_%s_%s.pcap"%(pcap_path, PORT, n)
tcpproc1 =  subprocess.Popen(["sudo tcpdump -i any port %s -w %s &"%(PORT,  pcapfile1)], shell=True, preexec_fn=os.setsid)

while True:
    try:
        l = input()
    except KeyboardInterrupt:
        pid = l.split(" ")[1] # FINISH "PID"
        os.system("sudo kill -9 " + pid)
        os.killpg(os.getpgid(tcpproc1.pid), signal.SIGTERM)
        exit_program = True
        break
    except Exception as e:
        print("error", e)
        break
        
os.killpg(os.getpgid(tcpproc1.pid), signal.SIGTERM)