# -*- coding: utf-8 -*-
"""
    nicm.status
    ~~~~~~~~~~~

    Status code definitions.
"""

# this doesn't use smaller values to avoid collision with old-style
# statuslist values that may be defined differently; this way they will
# raise a clear error instead when used
OK = 100
BUSY = 101
ERROR = 102
UNKNOWN = 999

# dictionary mapping all status constants to their names
statuses = dict((v, k.lower()) for (k, v) in globals().iteritems()
                if isinstance(v, int))
