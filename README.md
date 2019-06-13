# kubescript

A bunch of utility scripts to facilitate development/testing/debugging for k8s.

Sample Use Cases:
```
$ cd /tmp
$ git clone https://github.com/freehan/kubescript.git
$ cd kubescript

# dump iptables on all nodes in the cluster
$ ./kexec --all kube-proxy iptables-save

# ssh to VM without copy&paste stuff
$ ./gssh

# push a new version of kubelet to a node
# YES! No need to recreate the cluster!
$ ./pushkubelet

# push a new version of scheduler to master
./pushmaster kube-scheduler

# run a debug pod daemonset
$ kubectl apply -f image/debug-daemonset.yaml

# ssh to one of the debug pod and mess with stuff
$ ./kexec -all debug
```