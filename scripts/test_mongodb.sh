#!/bin/bash
echo "Testing MongoDB Connection to $1"
mongo --host $1:27017 --eval "db.stats()"
