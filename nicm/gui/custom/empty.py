#
# ANC empty customization file
#
# (c) 2009 by Georg Brandl
#

# -- general configuration -----------------------------------------------------

# name of this custom configuration
CUSTOMNAME = '(empty)'

# -- values for proposal/sample/archival tool ----------------------------------

# path for tcs files
TCSPATH = '/data/scripts'

# paths for logfile archival
NICMLOGPATH = '/data/log'
DAEMONLOGPATH = '/data/log/daemon'

# general file finding function: return all data files from the specified
# proposal number and time span (given as (year, month, day) tuples)
def DATA_FILES(propnr, datefrom, dateuntil):
    return []

# does the system support saved adjustments?
HAS_SAVED_ADJUSTS = False

# mutually exclusive instrument configurations
INSTRUMENTS = []
# commands for init file to set one of the instrument configurations
INSTRUMENT_COMMANDS = []
# nonexclusive optional add-ons
OPTIONS = []

# values are: (instrument, options, defaultinwhichlist, needscreation)
# where instrument is an index into INSTRUMENTS, or -1 for "all"
#       options is a list of indices into OPTIONS, or empty if default
#       defaultinwhichlist determines if the device is on by default in the
#         "file header", "once for each point" and "continuous logging" lists
#       needscreation is true if the device needs a NicmCreate

DEVICES = {
}

# from tas_globals.py
TASOPMODELIST = [
]

ETRANSFERUNITS = []

# -- values for scan input -----------------------------------------------------

# devices for sscan and cscan: name and unit
SCANDEVICES = [
]

# devices for ttscan
TTSCANDEVICES = [
]

# -- estimation functions ------------------------------------------------------

ANALYZERS = {
}

MOVE_ANALYZERS = {
}

# -- maintenance commands ------------------------------------------------------

MAINT_COMMANDS = [
]

# ------------------------------------------------------------------------------
