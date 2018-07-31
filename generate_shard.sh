#!/bin/sh
start=$1
end=$2
shift
shift
for idx in $(seq $start $end); do
    sed -e "s/\$idx/$idx/g" $@
done
