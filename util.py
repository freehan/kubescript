import os
import shutil
import subprocess

GET_ALL_RESOURCE = "kubectl get {} --all-namespaces -o wide"
GET_CURRENT_CONTEXT = "kubectl config current-context"
KUBECTL_RESOURCE_OPERATION = "kubectl {} {} --namespace={} {} {}"
KUBECTL_CREATE = "kubectl create -f "
KUBECTL_DELETE = "kubectl delete -f "
GET_ALL_GCE_INSTANCES = "gcloud compute instances list"
GCLOUD_SSH = ["gcloud", "compute", "ssh", "--zone"]
GCLOUD_COPY_FILE = ["gcloud", "compute", "scp"]
KUBE_BASE_IMAGE = "gcr.io/google_containers/debian-iptables-amd64:v4"
TMP_DOCKER_BUILD_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "build")
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


def get_all_resource(resource):
    return subprocess.check_output(GET_ALL_RESOURCE.format(resource), shell=True, universal_newlines=True)


def get_matched_objects(resource, prefix):
    output = get_all_resource(resource)
    lines = output.splitlines()
    objects = [lines[0]]
    for line in lines[1:]:
        cols = line.split()
        # assume 2nd column is name, 1st column is namespace
        if prefix == None or prefix == "" or cols[1].lstrip().startswith(prefix):
            objects.append(line)
    return objects


def get_all_pods():
    output = get_all_resource("pods")
    pods = []
    for line in output.splitlines()[1:]:
        cols = line.split()
        pods.append(Pod(cols[0], cols[1], cols[6], cols[7], cols[3]))
    return pods


def find_all_pods_with_prefix(pods, prefix):
    ret = [p for p in pods if p.name.startswith(prefix)]
    return ret


def run_kubectl(operation, resource, namespace, name, parameters):
    cmd = KUBECTL_RESOURCE_OPERATION.format(operation, resource, namespace, name, ' '.join(parameters))
    print("+ " + cmd)
    print(subprocess.check_output(cmd, shell=True, universal_newlines=True))


def exec_in_pod(pod, args):
    print("##### Exec in %s/%s" % (pod.namespace, pod.name))
    cmd = ["kubectl", "--namespace", pod.namespace, "exec"]
    if len(args) <= 1 and (args[0] == "bash" or args[0] == "sh"):
        cmd.append("-it")
    else:
        cmd.append("-t")
    cmd.append(pod.name)
    if args[0] == '-c':
        cmd += [args[0], args[1], "--" + args[2:]]
    else:
        cmd.append("--")
        cmd += args
    exec_cmd(cmd)


def get_kube_context():
    return subprocess.check_output(GET_CURRENT_CONTEXT, shell=True, universal_newlines=True)


def get_all_gce_instances():
    output = subprocess.check_output(GET_ALL_GCE_INSTANCES, shell=True, universal_newlines=True)
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
        instance = instances[int(i)]
    else:
        # only return instance name and
        # assume the instance is at us-central1-b
        instance = GCEInstance(host, 'us-central1-b', "", "", "")
    return instance


def gcloud_compute_ssh(zone, host):
    exec_cmd(GCLOUD_SSH + [zone, host])


def gcloud_compute_ssh_command(zone, host, cmd):
    exec_cmd(GCLOUD_SSH + [zone, host] + ["--command", cmd])


def gcloud_compute_copy_file_to_host(host, file):
    exec_cmd(GCLOUD_COPY_FILE + [file, host + ":"])


def exec_cmd(cmd):
    print("+ " + ' '.join(cmd))
    subprocess.call(cmd)


# assumes input command returns a table
def get_cmd_result_as_table(cmd):
    table = []
    output = ""
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
    except subprocess.CalledProcessError as exc:
        output = "Failed to exec: " + cmd + "\n"
        output += "ErrorCode: " + str(exc.returncode) + "\n"
        output += "Output: " + exc.output + "\n"
        print(output)
        return [[output]]

    lines = output.splitlines()
    for line in lines:
        table.append(line.split())
    return table


def convert_table_into_html(cmd, table):
    html = """
<div class="table-responsive col-md-6">
    <h4><b>{}</b></h4>
    <table class=\"table table-striped table-bordered table-hover table-condensed\">
        <tbody>
            {}
        </tbody>
    </table>
</div>
    """
    html_table = ""
    for line in table:
        html_table += "<tr>\n"
        items = ["<td>" + item + "</td>" for item in line]
        html_table += "\n".join(items)
        html_table += "</tr>\n"
    return html.format(cmd, html_table)


def build_kube_image(baseimage, binary_path, binary_name, tag="mykubetag"):
    if os.path.exists(TMP_DOCKER_BUILD_PATH):
        shutil.rmtree(TMP_DOCKER_BUILD_PATH)
    os.makedirs(TMP_DOCKER_BUILD_PATH)

    simlink_path = os.path.join(TMP_DOCKER_BUILD_PATH, binary_name)
    exec_cmd(["ln", binary_path, simlink_path])

    f = open(TMP_DOCKER_FILE_PATH, 'w+')
    f.write("FROM " + "--platform=linux/amd64 " + baseimage + "\n")
    # f.write("FROM " + baseimage + "\n")
    f.write("COPY " + binary_name + " /usr/local/bin/" + binary_name + "\n")
    f.close()
    exec_cmd(["docker", "build", "--pull", "-q", "-t", tag, TMP_DOCKER_BUILD_PATH])
    shutil.rmtree(TMP_DOCKER_BUILD_PATH)


def docker_rmi(tag):
    exec_cmd(["docker", "rmi", tag])


def build_kube_image_tarball(tag, output_path="/tmp/out.tar"):
    f = open(output_path, 'w+')
    subprocess.call(["docker", "save", tag], stdout=f)
    f.close()
    print("Saved %s image at %s" % (tag, output_path))
    # save tag
    f = open(output_path + ".tag", 'w+')
    f.write(tag)
    f.close()


def retrieve_image_tag(output_path):
    f = open(output_path + ".tag", "r")
    tag = f.read().replace('\n', '')
    f.close()
    return tag


mac_build_command = "KUBE_BUILD_PLATFORMS=linux/amd64 make all WHAT=${binary}"

def search_binary_in_k8s_output_path(binary):
    gopath = os.environ['GOPATH']
    bin_path = os.path.join(gopath, 'src/k8s.io/kubernetes/_output/local/bin/linux/amd64', binary)
    if not os.path.isfile(bin_path):
        raise LookupError("Cannot find %s binary in %s. If on mac, please build the binary with the following command:\n %s" % (binary, bin_path, mac_build_command))
    print("================Found %s Binary================" % binary)
    exec_cmd(["ls", "-al", bin_path])
    return bin_path


def ensure_tmp_path(path=os.path.join(os.path.dirname(os.path.realpath(__file__)), "tmp")):
    if os.path.exists(path):
        shutil.rmtree(path)
    return path
