from datetime import datetime
import re
import subprocess
import json
import argparse

PROJECT = "TO BE FILLED"
ZONE = "TO BE FILLED"
NEG_NAME = "TO BE FILLED"
BM_URL = "TO BE FILLED"
SEARCH = "TO BE FILLED"

VMs = {
    "vm1": "1.2.3.5",
    "vm2": "1.2.3.4",
}

NEG_ADD_DEL_FORMAT = 'curl -H "$(oauth2l header userinfo.email)" ' \
                     'https://www.googleapis.com/compute/staging_beta/projects/{}/zones/{}/networkEndpointGroups/{}/{} ' \
                     '-H "Content-Type:application/json" -d \'{}\''

ATTACH = "attachNetworkEndpoints"
DETACH = "detachNetworkEndpoints"

parser = argparse.ArgumentParser(description='NEG API latency test')
parser.add_argument('--expect-count', metavar='expect_count', type=int, default=10000)
parser.add_argument('--port-start', metavar='port_start', type=int, default=10000)
parser.add_argument('--port-per-vm', metavar='port_per_vm', type=int, default=1000)
group = parser.add_mutually_exclusive_group()
group.add_argument('--attach', action='store_true')
group.add_argument('--detach', action='store_true')
parser.set_defaults(attach=True)
args = parser.parse_args()

OPERATION = ""
if args.attach:
    OPERATION = ATTACH
else:
    OPERATION = DETACH

EXPECT_COUNT = args.expect_count
PORT_START = args.port_start
PORT_NUM = args.port_per_vm


print "OPERATION =", OPERATION
print "EXPECT_COUNT =", EXPECT_COUNT
print "PORT_START =", PORT_START
print "PORT_NUM =", PORT_NUM
print "TOTAL_ENDPOINT =", len(VMs)*PORT_NUM
# exit()

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
    print "START"

    endpointCount = 0
    for vm, ip in VMs.items():
        count = 0
        endpointList = []
        for port in range(PORT_START, PORT_START + PORT_NUM):
            endpointList.append(json.dumps(NetworkEndpoint(vm, ip, port).__dict__))
            endpointCount += 1
            count += 1
            if count >= 500:
                negCalls.append(genBody(endpointList))
                endpointList = []
                count = 0
        if len(endpointList) > 0:
            negCalls.append(genBody(endpointList))

    print "==========Number of calls=========:", len(negCalls)
    print "==========Number of Endpoints=========:", endpointCount

    t1 = datetime.now()

    for b in negCalls:
        subprocess.Popen("echo start; sleep 2; echo yeah", stderr=subprocess.STDOUT, shell=True)
        # subprocess.Popen(attachNE(b), stderr=subprocess.STDOUT, shell=True)
        # subprocess.Popen(detachNE(b), stderr=subprocess.STDOUT, shell=True)
        # subprocess.Popen(NEGCall(OPERATION, b), stderr=subprocess.STDOUT, shell=True)

    t2 = datetime.now()
    delta = t2 - t1
    combined1 = delta.seconds + delta.microseconds / 1E6
    while True:
        out = subprocess.check_output("gosso --url " + BM_URL, stderr=subprocess.STDOUT, shell=True)
        m = re.search(SEARCH, out)
        if m:
            found = m.group(1)
            print "Healthy endpoint count:" + found
            if int(found) >= EXPECT_COUNT:
                break
        else:
            print "no match"

    t3 = datetime.now()
    delta = t3 - t2
    combined2 = delta.seconds + delta.microseconds / 1E6

    print "NEG API calls completed in: " + str(combined1)
    print "Backend programmed in: " + str(combined2)
    print "END"
