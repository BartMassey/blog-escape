#!/usr/bin/python3
# Copyright (c) 2017 Bart Massey
# This work is available under the "MIT license".
# Please see the file COPYING in this distribution
# for license terms.

# Format Markdown content.

import mistune

from filter_autop import filter_autop
from filter_urlclean import filter_urlclean

markdown = mistune.Markdown()

# Return a properly-formatted version of
# the given Markdown content.
def format_md(content, sitename, title):
    content = markdown(content)
    return filter_urlclean(content, sitename)
