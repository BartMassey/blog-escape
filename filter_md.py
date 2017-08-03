#!/usr/bin/python3
# Copyright (c) 2017 Bart Massey
# This work is available under the "MIT license".
# Please see the file COPYING in this distribution
# for license terms.

# Format Markdown content.

import mistune

markdown = mistune.Markdown()

# Return a properly-formatted version of
# the given Markdown content.
def filter_md(content, **settings):
    return markdown(content)
