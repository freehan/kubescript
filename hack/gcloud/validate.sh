#!/bin/bash

# This script validates if the total count of endpoints in a list of NEGs are expected.
# Before executing this script, please make sure gcloud config is correct.
# Please note all NEGs in the same cluster has the same prefix.
NEG_PREFIX=$1

echo "Total endpoints in NEGs with prefix $1:"
gcloud compute network-endpoint-groups list | grep $NEG_PREFIX | awk '{sum += $4} END {print sum}'