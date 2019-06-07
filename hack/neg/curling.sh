#!/bin/bash

IP="tobeadd"

while :
do
  date
  curl --connect-timeout 1 -s ${IP} && echo
done
