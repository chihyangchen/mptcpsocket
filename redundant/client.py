#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import time
import threading
import datetime as dt
import select
import sys
import os
import queue
import argparse
import subprocess
import re
import numpy as np

HOST = '140.112.20.183'

def get_network_interface_list():
    pipe = subprocess.Popen('ifconfig', stdout=subprocess.PIPE, shell=True)
    text = pipe.communicate()[0].decode()
    l = text.split('\n')
    network_interface_list = []
    for x in l:
        if r"RUNNING" in x and 'lo' not in x:
            print(x[:x.find(':')])
            network_interface_list.append(x[:x.find(':')])
    network_interface_list = sorted(network_interface_list)
    return network_interface_list
network_interface_list = get_network_interface_list()
print(network_interface_list)

num_ports = len(network_interface_list)
UL_ports = np.arange(3270, 3270+2*num_ports, 2)
DL_ports = np.arange(3271, 3271+2*num_ports, 2)


thread_stop = False
exit_program = False
length_packet = 362
bandwidth = 5000*1024
total_time = 3600
expected_packet_per_sec = bandwidth / (length_packet << 3)
sleeptime = 1.0 / expected_packet_per_sec
prev_sleeptime = sleeptime
pcap_path = "pcapdir"
exitprogram = False
TCP_CONGESTION = 13   # defined in /usr/include/netinet/tcp.h
cong = 'cubic'.encode()
ss_dir = "ss"

def get_ss(port):
    now = dt.datetime.today()
    n = '-'.join([str(x) for x in[ now.year, now.month, now.day, now.hour, now.minute, now.second]])
    f = open(os.path.join(ss_dir, n) + '.csv', 'a+')
    while not thread_stop:
        proc = subprocess.Popen(["ss -it dst :%d"%(port)], stdout=subprocess.PIPE, shell=True)
        line = proc.stdout.readline()
        line = proc.stdout.readline()
        line = proc.stdout.readline().decode().strip()
        f.write(",".join([str(dt.datetime.now())]+ re.split("[: \n\t]", line))+'\n')
        time.sleep(1)
    f.close()

def connection_setup(host, port, result):
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_tcp.setsockopt(socket.IPPROTO_TCP, TCP_CONGESTION, cong)
    s_tcp.settimeout(10)
    s_tcp.connect((host, port))

    while True:
        print("%d wait for starting..."%(port))
        try:
            indata = s_tcp.recv(65535)
            if indata == b'START':
                print("START")
                break
            else:
                print("WTF", indata)
                break
        except Exception as inst:
            print("Error: ", inst)

    result[0] = s_tcp

def transmision(stcp_list):
    print("start transmision", stcp_list)
    i = 0
    prev_transmit = 0
    ok = (1).to_bytes(1, 'big')
    start_time = time.time()
    count = 1
    sleeptime = 1.0 / expected_packet_per_sec
    prev_sleeptime = sleeptime
    global thread_stop
    while time.time() - start_time < total_time and not thread_stop:
        try:
            t = time.time()
            t = int(t*1000).to_bytes(8, 'big')
            z = i.to_bytes(4, 'big')
            redundent = os.urandom(length_packet-12-1)
            outdata = t + z + ok +redundent
            for j in range(len(stcp_list)):
                stcp_list[j].sendall(outdata)
            i += 1
            time.sleep(sleeptime)
            if time.time()-start_time > count:
                print("[%d-%d]"%(count-1, count), "transmit", i-prev_transmit)
                count += 1
                sleeptime = prev_sleeptime / expected_packet_per_sec * (i-prev_transmit) # adjust sleep time dynamically
                prev_transmit = i
                prev_sleeptime = sleeptime
        except:
            break    
    print("---transmision timeout---")
    print("transmit", i, "packets")


def receive(s_tcp, port):
    s_tcp.settimeout(10)
    print("wait for indata...")
    start_time = time.time()
    count = 1
    capture_bytes = 0
    global thread_stop
    global buffer
    buffer = queue.Queue()
    while not thread_stop:
        try:
            indata = s_tcp.recv(65535)
            capture_bytes += len(indata)
            if time.time()-start_time > count:
                if capture_bytes <= 1024*1024:
                    print(port, "[%d-%d]"%(count-1, count), "%g kbps"%(capture_bytes/1024*8))
                else:
                    print(port, "[%d-%d]"%(count-1, count), "%gMbps" %(capture_bytes/1024/1024*8))
                count += 1
                capture_bytes = 0
        except Exception as inst:
            print("Error: ", inst)
            thread_stop = True
    thread_stop = True
    if capture_bytes <= 1024*1024:
        print(port, "[%d-%d]"%(count-1, count), "%g kbps"%(capture_bytes/1024*8))
    else:
        print(port, "[%d-%d]"%(count-1, count), "%gMbps" %(capture_bytes/1024/1024*8))
    print("---Experiment Complete---")
    print("STOP receiving")


if not os.path.exists(pcap_path):
    os.system("mkdir %s"%(pcap_path))


while not exitprogram:

    try:
        x = input("Press Enter to start\n")
        if x == "EXIT":
            break
        now = dt.datetime.today()

        n = [str(x) for x in[ now.year, now.month, now.day, now.hour, now.minute, now.second]]
        for i in range(len(n)-3, len(n)):
            if len(n[i]) < 2:
                n[i] = '0' + n[i]
        n = '-'.join(n)

        UL_pcapfiles = []
        DL_pcapfiles = []
        tcp_UL_proc = []
        tcp_DL_proc = []
        for p in UL_ports:
            UL_pcapfiles.append("%s/client_UL_%s_%s.pcap"%(pcap_path, p, n))
        for p in DL_ports:
            UL_pcapfiles.append("%s/client_DL_%s_%s.pcap"%(pcap_path, p, n))

        for p, pcapfile in zip(UL_ports, UL_pcapfiles):
            tcp_UL_proc.append(subprocess.Popen(["tcpdump -i any port %s -w %s &"%(p,  pcapfile)], shell=True, preexec_fn=os.setsid))

        for p, pcapfile in zip(DL_ports, DL_pcapfiles):
            tcp_UL_proc.append(subprocess.Popen(["tcpdump -i any port %s -w %s &"%(p,  pcapfile)], shell=True, preexec_fn=os.setsid))

        thread_list = []
        UL_result_list = []
        DL_result_list = []

        UL_tcp_list = [None] * num_ports
        DL_tcp_list = [None] * num_ports

        for i in range(num_ports):
            UL_result_list.append([None])
            DL_result_list.append([None])

        for i in range(len(UL_ports)):
            thread_list.append(threading.Thread(target = connection_setup, args = (HOST, UL_ports[i], UL_result_list[i])))

        for i in range(len(DL_ports)):
            thread_list.append(threading.Thread(target = connection_setup, args = (HOST, DL_ports[i], DL_result_list[i])))
        
        for i in range(len(thread_list)):
            thread_list[i].start()

        for i in range(len(thread_list)):
            thread_list[i].join()

        for i in range(num_ports):
            UL_tcp_list[i] = UL_result_list[i][0]
            DL_tcp_list[i] = DL_result_list[i][0]

        print("UL_tcp_list", UL_tcp_list)
        print("DL_tcp_list", DL_tcp_list)

        for i in range(num_ports):
            assert(UL_tcp_list[i] != None)
            assert(DL_tcp_list[i] != None)

    except Exception as inst:
        print("Error: ", inst)
        os.system("pkill tcpdump")
        continue
    thread_stop = False

    thread_stop = False
    transmision_thread = threading.Thread(target = transmision, args = (UL_tcp_list, ))
    recive_thread_list = []
    for i in range(num_ports):
        recive_thread_list.append(threading.Thread(target = receive, args = (DL_tcp_list[i], DL_ports[i])))



    # t3 = threading.Thread(target=get_ss, args=(PORT, ))
    # t4 = threading.Thread(target=get_ss, args=(PORT2, ))

    # t3.start()
    # t4.start()
    try:
        transmision_thread.start()
        for i in range(len(recive_thread_list)):
            recive_thread_list[i].start()
        transmision_thread.join()
        for i in range(len(recive_thread_list)):
            recive_thread_list[i].join()

        while transmision_thread.is_alive():
            x = input("Enter STOP to Stop\n")
            if x == "STOP":
                thread_stop = True
                break
            elif x == "EXIT":
                thread_stop = True
                exitprogram = True
        thread_stop = True
        # t3.join()
        # t4.join()


    except Exception as inst:
        print("Error: ", inst)
    except KeyboardInterrupt:
        print("finish")

    finally:
        thread_stop = True
        for i in range(num_ports):
            UL_tcp_list[i].close()
            DL_tcp_list[i].close()
        os.system("killall -9 tcpdump")
