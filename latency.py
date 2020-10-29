#!/usr/bin/python
import argparse
import json
import re
import subprocess
from datetime import datetime

PROJECT = "TO BE FILLED"
ZONE = "TO BE FILLED"
NEG_NAME = "TO BE FILLED"
BM_URL = 'TO BE FILLED'
SEARCH = 'TO BE FILLED'
VMs = {
    "VM1": "IP1",
    "VM2": "IP2"
}

NEG_ADD_DEL_FORMAT = 'curl -H "$(oauth2l header userinfo.email)" ' \
                     'https://www.googleapis.com/compute/beta/projects/{}/zones/{}/networkEndpointGroups/{}/{} ' \
                     '-H "Content-Type:application/json" -d \'{}\''

ATTACH = "attachNetworkEndpoints"
DETACH = "detachNetworkEndpoints"

parser = argparse.ArgumentParser(description='NEG API latency test')
parser.add_argument('--expect-count', metavar='expect_count', type=int, default=10000)
parser.add_argument('--port-start', metavar='port_start', type=int, default=10000)
parser.add_argument('--port-per-vm', metavar='port_per_vm', type=int, default=1000)
parser.add_argument('--vm-num', metavar='vm_num', type=int, default=-1)
group = parser.add_mutually_exclusive_group()
group.add_argument('--attach', action='store_true')
group.add_argument('--detach', action='store_true')
args = parser.parse_args()

print
args.attach
print
args.detach

OPERATION = ""
if args.detach:
    OPERATION = DETACH
else:
    OPERATION = ATTACH
EXPECT_COUNT = args.expect_count
PORT_START = args.port_start
PORT_NUM = args.port_per_vm
VM_NUM = args.vm_num

print
"OPERATION =", OPERATION
print
"EXPECT_COUNT =", EXPECT_COUNT
print
"PORT_START =", PORT_START
print
"PORT_NUM =", PORT_NUM
print
"VM_NUM =", VM_NUM
print
"TOTAL_ENDPOINT =", len(VMs) * PORT_NUM


def NEGCall(operation, body):
    return NEG_ADD_DEL_FORMAT.format(PROJECT, ZONE, NEG_NAME, operation, body)


def attachNE(body):
    return NEG_ADD_DEL_FORMAT.format(PROJECT, ZONE, NEG_NAME, ATTACH, body)


def detachNE(body):
    return NEG_ADD_DEL_FORMAT.format(PROJECT, ZONE, NEG_NAME, DETACH, body)


class NetworkEndpoint:
    def __init__(self, instance, ipAddress, port):
        self.instance = instance
        self.ipAddress = ipAddress
        self.port = port
        pass


def genBody(endpoints):
    res = ', '.join(endpoints)
    return '{"networkEndpoints": [' + res + ']}'


# Generated body
negCalls = []

if __name__ == "__main__":
    print
    "START"

    endpointCount = 0
    endpointList = []
    curCount = 0
    vmCount = 0
    for vm, ip in VMs.items():
        vmCount += 1
        if VM_NUM != -1 and vmCount > VM_NUM:
            break
        for port in range(PORT_START, PORT_START + PORT_NUM):
            endpointList.append(json.dumps(NetworkEndpoint(vm, ip, port).__dict__))
            endpointCount += 1
            curCount += 1
            if curCount >= 500:
                negCalls.append(genBody(endpointList))
                endpointList = []
                curCount = 0
    if len(endpointList) > 0:
        negCalls.append(genBody(endpointList))

    print
    "==========Number of calls=========:", len(negCalls)
    print
    "==========Number of Endpoints=========:", endpointCount

    t1 = datetime.now()

    for b in negCalls:
        subprocess.Popen(NEGCall(OPERATION, b), stderr=subprocess.STDOUT, shell=True)

    t2 = datetime.now()
    delta = t2 - t1
    combined1 = delta.seconds + delta.microseconds / 1E6
    while True:
        out = subprocess.check_output("gosso --url " + BM_URL, stderr=subprocess.STDOUT, shell=True)
        # print out
        m = re.search(SEARCH, out)
        #    print m.group(0)

        if m:
            found = m.group(1)
            print
            "Healthy endpoint count:" + found
            if int(found) == EXPECT_COUNT:
                break
        else:
            print
            "no match"

    t3 = datetime.now()
    delta = t3 - t2
    combined2 = delta.seconds + delta.microseconds / 1E6

    print
    "NEG API calls issued in: " + str(combined1)
    print
    "Backend programmed in: " + str(combined2)
    print
    "END"
