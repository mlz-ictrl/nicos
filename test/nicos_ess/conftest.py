import sys
import os

# no testing under Python 2 required
if sys.version_info[0] == 2:
    collect_ignore = os.listdir(os.path.dirname(__file__))
