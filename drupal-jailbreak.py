#!/usr/bin/python3
# Copyright (c) 2017 Bart Massey

# Pull the content out of a Drupal site into
# portable formats.

import MySQLdb
db = MySQLdb.connect(user="drupal_fob",
                     db="drupal_fob",
                     read_default_file="~/.drupal_jailbreak.my.cnf")

c = db.cursor()
c.execute("SELECT nid FROM node")
for nid, in c:
    print(nid)
