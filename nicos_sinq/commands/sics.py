""" SICS equivalent NICOS commands
"""

from nicos.commands.device import adjust, maw
from nicos.commands.scan import timescan

# Equivalent of sics dr (drive) command
dr = maw

# Equvalent of sics setposition/sp command
setposition = sp = adjust

# Equivalent of sics repeat command
repeat = timescan
