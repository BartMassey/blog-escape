#!/bin/sh
# Copyright © 2017 Bart Massey
#
# Apply all repair scripts to each content file to make
# browsable content.
if [ $# -ne 1 ]
then
    echo "fix-urls: usage: fix-urls <base-url>" >&2
    exit 1
fi
BASE_URL="$1"
if [ -d node ]
then
    rm -rf node/*
else
    mkdir node
fi
for c in content/*.html
do
    BASENAME="`basename $c`"
    sh scripts/fix-urls.sh "$BASE_URL" <$c >node/"$BASENAME"
done
