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

parser = argparse.ArgumentParser()
parser.add_argument("-p1", "--port1", type=int,
                    help="port to bind", default=3271)
args = parser.parse_args()

PORT = args.port1           # UL

thread_stop = False
exit_program = False
length_packet = 362
cong_algorithm = 'cubic'
pcap_path = "/home/wmnlab/D/pcap_data"
cong = 'reno'.encode()

now = dt.datetime.today()
n = '-'.join([str(x) for x in[ now.year, now.month, now.day, now.hour, now.minute, now.second]])

pcapfile1 = "%s/DL_%s_%s.pcap"%(pcap_path, PORT, n)
filename = "sr_port_%s_running.tmp"%(PORT)
os.system("echo \"idle\" > %s"%(filename))
tcpproc1 =  subprocess.Popen(["tcpdump -i any port %s -w %s &"%(PORT,  pcapfile1)], shell=True, preexec_fn=os.setsid)
socket_proc =  subprocess.Popen(["iperf3 -s -B 0.0.0.0 -p %d"%(PORT)], shell=True, preexec_fn=os.setsid)
time.sleep(1)
while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        os.killpg(os.getpgid(socket_proc.pid), signal.SIGTERM)
        os.killpg(os.getpgid(tcpproc1.pid), signal.SIGTERM)
        break
    except Exception as e:
        print("error", e)
os.system("killall -9 iperf3")
os.killpg(os.getpgid(tcpproc1.pid), signal.SIGTERM)
