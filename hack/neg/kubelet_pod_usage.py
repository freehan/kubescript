#!/usr/bin/env python
# get pods cpu/memory usage from kubelet
# ref:
# https://github.com/kubernetes/kubernetes/blob/master/pkg/kubelet/apis/stats/v1alpha1/types.go
# CPU sample window: around 15 seconds
# https://github.com/kubernetes/kubernetes/blob/release-1.14/pkg/kubelet/cadvisor/cadvisor_linux.go#L50


import urllib2
import json
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("pods", help="pod names seperate by comma")

args = parser.parse_args()
pods = args.pods.split(",")

files = {}
for p in pods:
  f = open("%s-usage.txt" % p, "a", buffering=1)
  files[p] = f
  out = "Time \t workingSetMBs \t usageMBs \t usageMillisecondCores \t usageCoreMilliseconds \n"
  f.write(out)

while True:
  summary = urllib2.urlopen("http://localhost:10255/stats/summary").read()
  data = json.loads(summary)
  for pod in data["pods"]:
    pname = pod["podRef"]["name"]
    for targetName in pods:
      if pname.startswith(targetName):
        out = "%s \t %fMbs \t %fMbs \t %sms \t %sms \n" % (pod["memory"]["time"], 
                                                         float(pod["memory"]["workingSetBytes"])/1024/1024, 
                                                         float(pod["memory"]["usageBytes"])/1024/1024, 
                                                         float(pod["cpu"]["usageNanoCores"])/1000000, 
                                                         float(pod["cpu"]["usageCoreNanoSeconds"])/1000000)
        files[targetName].write(out)

  time.sleep(15)
