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
def memoize_re(expr, flags=0):
    global re_exprs
    if expr in re_exprs:
        return re_exprs[expr]
    rc = re.compile(expr, flags=flags)
    re_exprs[expr] = rc
    return rc
    
# Memoized split.
def re_split(expr, *args, maxsplit=0, flags=0):
    return memoize_re(expr, flags=flags).split(*args, maxsplit=maxsplit)

# Memoized sub.
def re_sub(expr, *args, count=0, flags=0):
    return memoize_re(expr, flags=flags).sub(*args, count=count)

# Memoized subn.
def re_subn(expr, *args, count=0, flags=0):
    return memoize_re(expr, flags=flags).subn(*args, count=count)

# Memoized match.
def re_match(expr, *args, flags=0):
    return memoize_re(expr, flags=flags).match(*args)

# Memoized search.
def re_search(expr, *args, flags=0):
    return memoize_re(expr, flags=flags).match(*args)
