# Copyright (c) 2017 Bart Massey
# This work is available under the "MIT license".
# Please see the file COPYING in this distribution
# for license terms.

# Make a print()-style logger.

import sys

def make_logger(name, status):
    """Make a logger to stderr, closed over name and status."""
    def log(*args, **kwargs):
        if not status:
            return
        print(name + ":", *args, **kwargs, flush=True, file=sys.stderr)
    return log
