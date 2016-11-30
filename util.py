import subprocess
import os
import shutil
import datetime
from pprint import pprint

GET_ALL_PODS = ["kubectl", "get", "pods", "--all-namespaces", "-o", "wide", "--show-all"]
GET_ALL_GCE_INSTANCES = ["gcloud", "compute", "instances", "list"]
GCLOUD_SSH = ["gcloud", "compute", "ssh", "--zone"]
GCLOUD_COPY_FILE = ["gcloud", "compute", "copy-files"]
KUBE_BASE_IMAGE = "gcr.io/google_containers/debian-iptables-amd64:v4"
TMP_DOCKER_BUILD_PATH = "~/Desktop/tmp/mydockerbuild/"
DOCKERFILE = "Dockerfile"
TMP_DOCKER_FILE_PATH = os.path.join(TMP_DOCKER_BUILD_PATH, DOCKERFILE)


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


def get_target_gce_instance(host):
    if host == None:
        instances = get_all_gce_instances()
        i = input("Enter an instance index: ")
        instance = instances[i]
    else:
        # only return instance name and
        # assume the instance is at us-central1-b
        instance = GCEInstance()
        instance.name = host
        instance.zone = 'us-central1-b'
    return instance


def gcloud_compute_ssh(zone, host):
    exec_cmd(GCLOUD_SSH + [zone, host])


def gcloud_compute_ssh_command(zone, host, cmd):
    exec_cmd(GCLOUD_SSH + [zone, host] + ["--command", cmd])


def gcloud_compute_copy_file_to_host(host, file):
    exec_cmd(GCLOUD_COPY_FILE + [file, host + ":"])


def exec_cmd(cmd):
    print "+ " + ' '.join(cmd)
    subprocess.call(cmd)


def build_kube_image(baseimage, binary_path, binary_name, tag="mykubetag"):
    if os.path.exists(os.path.dirname(TMP_DOCKER_BUILD_PATH)):
        shutil.rmtree(TMP_DOCKER_BUILD_PATH)
    os.makedirs(os.path.dirname(TMP_DOCKER_BUILD_PATH))

    simlink_path = os.path.join(TMP_DOCKER_BUILD_PATH, binary_name)
    exec_cmd(["ln", binary_path, simlink_path])

    f = open(TMP_DOCKER_FILE_PATH, 'w+')
    f.write("FROM " + baseimage + "\n")
    f.write("ADD " + binary_name + " /usr/local/bin/" + binary_name + "\n")
    f.close()
    exec_cmd(["docker", "build", "-t", tag, TMP_DOCKER_BUILD_PATH])


def docker_rmi(tag):
    exec_cmd(["docker", "rmi", tag])


def build_kube_image_tarball(tag, output_path="/tmp/mydockerfile/out.tar"):
    f = open(output_path, 'w+')
    subprocess.call(["docker", "save", tag], stdout=f)
    f.close()

def search_binary_in_k8s_output_path(binary):
    gopath = os.environ['GOPATH']
    bin_path = os.path.join(gopath, 'src/k8s.io/kubernetes/_output/bin', binary)
    if not os.path.isfile(bin_path):
        raise Exception("Cannot find %s binary in %s" % (binary, bin_path))
    print "================Found %s Binary================" % binary
    exec_cmd(["ls", "-al", bin_path])
    return bin_path