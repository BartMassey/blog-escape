#!/usr/bin/python3
# Copyright (c) 2017 Bart Massey
# This work is available under the "MIT license".
# Please see the file COPYING in this distribution
# for license terms.

# Pull the content out of a Drupal site into
# portable formats.

import sys

import MySQLdb
import MySQLdb.cursors

# Connect to the database using the information specified
# in the cnf file.
db = MySQLdb.connect(read_default_file="~/.drupal_jailbreak.my.cnf")
c = db.cursor()

# Get the possible filter formats, which correspond
# to content body formats, matching a given pattern.
def get_formats(pattern):
    c = db.cursor()
    c.execute("""SELECT format FROM filter_format
                 WHERE upper(name) LIKE %s""", ("%" + pattern + "%",))
    return [fformat for fformat, in c]

format_types = [
    ("html", "HTML"), 
    ("md", "MARKDOWN"),
    ("txt", "TEXT"),
    ("php", "PHP"),
    ("bbcode", "BBCODE")
]

formats = dict()
for suffix, pattern in format_types:
    for fformat in get_formats(pattern):
        formats[fformat] = suffix

c.execute("""SELECT node.nid, node.title, field_data_body.body_value,
                    field_data_body.body_format
             FROM node JOIN field_data_body
             ON node.nid = field_data_body.entity_id
             WHERE node.type = \"blog\"""")
for nid, title, body, fformat in c:
    with open("node/%d.%s" % (nid, formats[fformat]), "w") as node_file:
        print("title: %s" % (title,), file=node_file)
        print(file=node_file)
        print(body, file=node_file)
