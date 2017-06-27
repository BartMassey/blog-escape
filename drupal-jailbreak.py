#!/usr/bin/python3
# Copyright (c) 2017 Bart Massey
# This work is available under the "MIT license".
# Please see the file COPYING in this distribution
# for license terms.

# Pull the content out of a Drupal site into
# portable formats.

import MySQLdb
import MySQLdb.cursors

db = MySQLdb.connect(user="drupal_fob",
                     db="drupal_fob",
                     read_default_file="~/.drupal_jailbreak.my.cnf",
                     cursorclass=MySQLdb.cursors.DictCursor)

c = db.cursor()
c.execute("SELECT * FROM node")
for node in c:
    print(node)
