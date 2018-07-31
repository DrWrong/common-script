#!/bin/sh

echo "Going to dump data from msvip"
pg_dump -a -t campaigns -t items -t products -t item_affiliate_products -d putong-payment -U postgres -h msvip.dev.p1staff.com > /tmp/data.sql
trap "rm -f /tmp/data.sql" EXIT


host=$1
if [ ! -n $host ]; then
    echo "Host is empty"
    exit 1
fi
port=${2-"6432"}
echo "Going to copy data to $host:$port"
echo "TRUNCATE TABLE campaigns; TRUNCATE TABLE items; TRUNCATE TABLE products; TRUNCATE TABLE item_affiliate_products"|psql -h $host -p $port  -U postgres -d putong-payment
echo "TRUNCATE TABLE OK"
psql -h $host -p $port -U postgres -d putong-payment -f /tmp/data.sql
