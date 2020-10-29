#!/usr/bin/python

import argparse

from util import *

parser = argparse.ArgumentParser(
    description='kubectl warpper to operate on one of the resource that match prefix across all namespaces. e.g. kk get pod kube -o yaml')
parser.add_argument("--all", dest='all', action='store_true',
                    help='exec in all matched pods')
parser.add_argument('operation', metavar='OPERATION', type=str, nargs=1,
                    help='kubectl operation. e.g. get')
parser.add_argument('resource', metavar='RESOURCE', type=str, nargs=1,
                    help='k8s resource type. e.g. pod')
parser.add_argument('prefix', metavar='PREFIX', type=str, nargs='?',
                    help='prefix of resource to target')
parser.set_defaults(all=False)

# unkonw arguments will be passed to kubectl
args, unknown_args = parser.parse_known_args()
resource = args.resource[0]
operation = args.operation[0]
prefix = args.prefix if args.prefix != None else ""

matches = get_matched_objects(resource, prefix)

if operation == 'get' and len(unknown_args) <= 0:
    print
    '\n'.join(matches)
    exit(0)

if len(matches) <= 1 or prefix == "":
    print
    'no match found'
    exit(1)

for obj in matches[1:]:
    fields = obj.split()
    run_kubectl(operation, resource, fields[0], fields[1], unknown_args)
    if not args.all:
        break
