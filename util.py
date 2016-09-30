import subprocess
from pprint import pprint

GET_ALL_PODS = ["kubectl", "get", "pods", "--all-namespaces", "-o", "wide", "--show-all"]
GET_ALL_GCE_INSTANCES = ["gcloud", "compute", "instances", "list"]
GCLOUD_SSH = ["gcloud", "compute", "ssh", "--zone"]
GCLOUD_COPY_FILE = ["gcloud", "compute", "copy-files"]

class Pod:
    def __init__(self):
        pass

    def __init__(self, namespace, name, ip, node, status):
        self.namespace = namespace
        self.name = name
        self.ip = ip
        self.node = node
        self.status = status
        pass

class GCEInstance:
    def __init__(self):
        pass

    def __init__(self, name, zone, internalip, externalip, status):
        self.name = name
        self.zone = zone
        self.internal_ip = internalip
        self.external_ip = externalip
        self.status = status
        pass

    def __str__(self):
        return self.name + '\t' + self.zone + '\t' + self.internal_ip + '\t' + self.external_ip + '\t' + self.status

def get_all_pods():
    output = subprocess.check_output(GET_ALL_PODS)
    pods = []
    for line in output.splitlines()[1:]:
        cols = line.split()
        pods.append(Pod(cols[0], cols[1], cols[6], cols[7], cols[3]))
    return pods

def find_pod_with_prefix(pods, prefix):
    for pod in pods:
        if pod.name.startswith(prefix):
            return pod
    return None

def find_all_pods_with_prefix(pods, prefix):
    ret = [p for p in pods if p.name.startswith(prefix)]
    return ret

def exec_in_pod(pod, commands):
    print("##### Exec in %s/%s" % (pod.namespace, pod.name))
    exec_cmd(["kubectl", "--namespace", pod.namespace, "exec", "-it", pod.name] + commands)

def get_all_gce_instances():
    output = subprocess.check_output(GET_ALL_GCE_INSTANCES)
    instances = []
    i = 0
    lines = output.splitlines()
    print("---\t %s" % lines[0])
    for line in lines[1:]:
        print("[%d] -\t %s" % (i, line))
        i += 1
        cols = line.split()
        instances.append(GCEInstance(cols[0], cols[1], cols[3], cols[4], cols[5], ))
    return instances

def gcloud_compute_ssh(zone, host):
    exec_cmd(GCLOUD_SSH + [zone, host])

def gcloud_compute_ssh_command(zone, host, cmd):
    exec_cmd(GCLOUD_SSH + [zone, host] + ["--command", cmd])

def gcloud_compute_copy_file_to_host(host, file):
    exec_cmd(GCLOUD_COPY_FILE + [file, host+":"])

def exec_cmd(cmd):
    print "+ " + ' '.join(cmd)
    subprocess.call(cmd)