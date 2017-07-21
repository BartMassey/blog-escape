#!/usr/bin/python3
# Copyright (c) 2017 Bart Massey
# This work is available under the "MIT license".
# Please see the file COPYING in this distribution
# for license terms.

# "Format" HTML content.

from filter_urlclean import filter_urlclean

# Return a properly-formatted version of
# the given HTML-ish content which needs auto
# line breaks.
def format_html(content, sitename):
    return filter_urlclean(content, sitename)
