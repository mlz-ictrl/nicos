import sys

# skip tests requiring Python 3 only dependency
if sys.version_info[0] == 2:
    collect_ignore = ['test_devices']
