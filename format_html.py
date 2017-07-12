#!/usr/bin/python3
# Copyright (c) 2017 Bart Massey
# This work is available under the "MIT license".
# Please see the file COPYING in this distribution
# for license terms.

# Format HTML content.

from filter_autop import filter_autop
from filter_urlclean import filter_urlclean

# Return a properly-formatted version of
# the given HTML(ish) content.
def format_html(content, sitename, title):
    urlclean = filter_urlclean(content, sitename)
    return filter_autop(urlclean)
