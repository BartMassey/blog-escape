# Copyright (c) 2017 Bart Massey
# This work is available under the "MIT license".
# Please see the file COPYING in this distribution
# for license terms.

# Loose port of Drupal's Smiley module to Python.

import re

from re_memo import *
from filters.xss import *

# Ported from Drupal smiley.module .
#   http://api.drupal.org/api/function/_filter_autop
# The text processing is pretty literal, the rest
# is pretty loose.
# 
# As with the original, this filter inserts IMG URLs for the
# Smileys. Unloke the original, a HEIGHT constraint is used
# to ensure that the smileys are of reasonable size.
# 
# Comments herein are from the original source, unless
# marked with BCM.

def filter_smiley(text, **settings):
    """Convert smileys in text to image URLs."""

    assert False
