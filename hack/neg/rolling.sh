#!/bin/bash

IP="add"
echo "Staring with VIP $IP"

for i in `seq 1 100000`
do
  echo "#################Trigger Rolling Update"
  date
  cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    run: hostname
  name: hostname
spec:
  selector:
    matchLabels:
      run: hostname
  strategy:
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
    type: RollingUpdate
  template:
    metadata:
      labels:
        run: hostname
      annotations:
        templateCreationTime: "`date`"
    spec:
      containers:
      - image: gcr.io/kubernetes-e2e-test-images/serve-hostname:1.1
        imagePullPolicy: IfNotPresent
        name: hostname
EOF

  sleep 300

  echo "#################Counting unique responses" 
  for i in `seq 1 100`; do curl --connect-timeout 1 -s ${IP} && echo;  done  |sort | uniq -c 
done
