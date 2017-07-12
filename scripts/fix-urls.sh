#!/bin/sh
# Copyright © 2017 Bart Massey
#
# Fix Drupal node URLs to be unprefixed for site portability.
if [ $# -ne 1 ]
then
    echo "fix-urls: usage: fix-urls <base-url>" >&2
    exit 1
fi
BASE_URL=`echo "$1" | sed 's/\./\\./g'`
sed \
  -e "s@\(href\|HREF\) *= *\"https\?://${BASE_URL}/\([^\"]*\)@href=\"/\\2@g" \
  -e "s@\(src\|SRC\) *= *\"https\?://${BASE_URL}/\([^\"]*\)@href=\"/\\1@g" \
  -e "s@href=\"/system/files/@href=\"/files/@g"
