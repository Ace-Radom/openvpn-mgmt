#!/bin/bash

length=256
key=""

while [ ${#key} -lt $length ]; do
    chunk=$(head -c 1024 /dev/random | tr -dc 'a-zA-Z0-9')
    key="$key$chunk"
done

echo "${key:0:$length}"
