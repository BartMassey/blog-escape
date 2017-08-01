#!/usr/bin/python3
# Copyright (c) 2017 Bart Massey
# This work is available under the "MIT license".
# Please see the file COPYING in this distribution
# for license terms.

# Format BBCode content.

import bbcode

parser = bbcode.Parser(replace_links=False, escape_html=False)

# Return a properly-formatted version of
# the given Markdown content.
def filter_bbcode(content, sitename, args):
    return parser.format(content)
