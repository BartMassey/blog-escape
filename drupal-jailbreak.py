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

db = MySQLdb.connect(read_default_file="~/.drupal_jailbreak.my.cnf")

c = db.cursor()
c.execute("""SELECT format, name FROM filter_format""")
formats = {fformat: fname for fformat, fname in c}
c.execute(
    """SELECT node.nid, node.title, field_data_body.body_value,
    field_data_body.body_format FROM
    node JOIN field_data_body ON node.nid = field_data_body.entity_id WHERE
    node.type = \"blog\"""")
for nid, title, body, format in c:
    with open("nodes/%d" % (nid,), "w") as node_file:
        print("title: %s" % (title,), file=node_file)
        print("format: %s" % (formats[format],), file=node_file)
        print(file=node_file)
        print(body, file=node_file)
