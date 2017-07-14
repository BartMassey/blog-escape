#!/usr/bin/python3
# Copyright (c) 2017 Bart Massey
# This work is available under the "MIT license".
# Please see the file COPYING in this distribution
# for license terms.

# Get a slight speedup by precompiling the
# regexes lazily and then looking them up
# on future calls.

import re

# Memo array.
re_exprs = dict()

# Function for memoizing a thing.
def memoize_re(expr):
    global re_exprs
    if expr in re_exprs:
        return re_exprs[expr]
    rc = re.compile(expr)
    re_exprs[expr] = rc
    return rc
    
# Memoized split.
def re_split(expr, *args):
    return memoize_re(expr).split(*args)

# Memoized sub.
def re_sub(expr, sub, value):
    return memoize_re(expr).sub(sub, value)

# Memoized search.
def re_search(expr, value):
    return memoize_re(expr).search(value)
