#!/usr/bin/python3
# Copyright (c) 2017 Bart Massey
# This work is available under the "MIT license".
# Please see the file COPYING in this distribution
# for license terms.

# Format BBCode content.

import bbcode

from filter_urlclean import filter_urlclean

parser = bbcode.Parser(replace_links=False, escape_html=False)

# Return a properly-formatted version of
# the given Markdown content.
def format_bbcode(content, sitename):
    content = parser.format(content)
    return filter_urlclean(content, sitename)
