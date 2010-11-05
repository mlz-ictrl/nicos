#!/usr/bin/env python

import sys

try:
    import nose
except ImportError:
    print 'The "nose" package is required to run this test suite.'
    sys.exit(1)
else:
    print 'Running nicm test suite...'
    print '-' * 70
    nose.main()
