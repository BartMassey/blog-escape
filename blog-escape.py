#!/usr/bin/python3
# Copyright (c) 2017 Bart Massey
# This work is available under the "MIT license".
# Please see the file COPYING in this distribution
# for license terms.

# Pull the content out of a Drupal site into
# portable formats.

import re

# Directory where raw content is to be stored.
content_dir = "content"

# Directory where processed content is to be stored.
node_dir = "node"

import sys
import os
import os.path as osp

import MySQLdb
import MySQLdb.cursors

from filter_nl import filter_nl
from format_html import format_html
from format_md import format_md
from format_bbcode import format_bbcode
from format_txt import format_txt

# Get the sitename from the command line.
assert len(sys.argv) == 2
sitename = sys.argv[1]

# Connect to the database using the information specified
# in the cnf file.
sitename_dashes = re.sub(r'\.', '-', sitename)
cwd = os.getcwd()
default_file = "%s/%s.my.cnf" % (cwd, sitename_dashes)
db = MySQLdb.connect(read_default_file=default_file)
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
    ("MARKDOWN", "md"),
    ("TEXT", "txt"),
    ("PHP", "php"),
    ("BBCODE", "bbcode")
]
formats = dict()
for pattern, suffix in format_types:
    for fformat in get_formats(pattern):
        formats[fformat] = suffix

# Empty or create the given directory.
def clean_dir(dir):
    if osp.isdir(dir):
        for fn in os.listdir(dir):
            os.remove(dir + "/" + fn)
    else:
        os.mkdir(dir)

# Clean the work directories.
clean_dir(content_dir)
clean_dir(node_dir)

# Set up the formatters.
formatters = {
    "html" : format_html,
    "md" : format_md,
    "bbcode" : format_bbcode,
    "txt" : format_txt
}

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
        ftype = formats[fformat]
        if ftype not in formatters:
            print("node %d: cannot format %s" % (nid, ftype))
            continue
        cfn = "%d.%s" % (nid, ftype)
        nfn = "%d.html" % (nid,)
    else:
        print("node %d: unknown format %s" % (nid, fformat))
        continue
    body = filter_nl(body)
    with open("%s/%s" % (content_dir, cfn), "w") as content_file:
        content_file.write(body)
    formatted = formatters[ftype](body, sitename, title)
    with open("%s/%s" % (node_dir, nfn), "w") as node_file:
        node_file.write(formatted)
