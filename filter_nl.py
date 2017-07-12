#!/usr/bin/python3
# Copyright (c) 2017 Bart Massey
# This work is available under the "MIT license".
# Please see the file COPYING in this distribution
# for license terms.

# Filter to rewrite line endings to UNIX format.

import re

# Rewrite newlines to UNIX format.
def filter_nl(content):
    # Rewrite DOS line endings.
    content = re.sub(r'\r\n', '\n', content)
    # Replace remaining CRs.
    content = re.sub(r'\r', '', content)
    # All done.
    return content
