#!/usr/bin/python3
# Copyright (c) 2017 Bart Massey
# This work is available under the "MIT license".
# Please see the file COPYING in this distribution
# for license terms.

# Pull the content out of a Drupal site into
# portable formats.

# Directory where content is to be stored.
output_dir = "content"

import sys
import os
import os.path as osp

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

# Build the format -> suffix dictionary.
format_types = [
    ("HTML", "html"), 
    ("EASY HTML", "htm"),
    ("MARKDOWN", "md"),
    ("TEXT", "txt"),
    ("PHP", "php"),
    ("BBCODE", "bbcode")
]
formats = dict()
for pattern, suffix in format_types:
    for fformat in get_formats(pattern):
        formats[fformat] = suffix

# Empty or create the output directory.
if osp.isdir(output_dir):
    for fn in os.listdir(output_dir):
        os.remove(output_dir + "/" + fn)
else:
    os.mkdir(output_dir)

# Extract node contents and store in files.
# Captions are represented in field_data_body with
# body_format NULL somehow.
c.execute("""SELECT node.nid, node.title, field_data_body.body_value,
                    field_data_body.body_format
             FROM node JOIN field_data_body
             ON node.nid = field_data_body.entity_id
             WHERE field_data_body.body_format IS NOT NULL""")
for nid, title, body, fformat in c:
    if fformat in formats:
        fn = "%s/%d.%s" % (output_dir, nid, formats[fformat])
    else:
        print("node %d: unknown format %s" % (nid, fformat))
        continue
    with open(fn, "w") as node_file:
        print("title: %s" % (title,), file=node_file)
        print(file=node_file)
        for line in body.splitlines():
            print(line, file=node_file)
