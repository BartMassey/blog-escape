# Copyright (c) 2017 Bart Massey
# This work is available under the "MIT license".
# Please see the file COPYING in this distribution
# for license terms.

# Version of Drupal's `filter_html()` and
# `filter_html_escape()` from `filter.module`.

import sys
import html

from filters.xss import *

ignored_nofollow = False

def filter_html(text, allowed_html,
                filter_html_help=None, filter_html_nofollow=0):
    global ignored_nofollow
    if filter_html_nofollow != 0 and not ignored_nofollow:
        print("filter_html: warning: cannot nofollow", file=sys.stderr)
        ignored_nofollow = True
    allowed_tags = re_split(r'\s+|<|>', allowed_html)
    allowed_tags = [t for t in allowed_tags if t != '']
    return filter_xss(text, allowed_tags=allowed_tags)

def filter_html_escape(text, **settings):
    return html.escape(text)
