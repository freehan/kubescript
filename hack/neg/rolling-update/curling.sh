#!/bin/bash

IP=$1

while :
do
  date
  curl --connect-timeout 1 -s ${IP} && echo
done
