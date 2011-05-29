#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""Empty customization for the GUI."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

# -- general configuration -----------------------------------------------------

# name of this custom configuration
CUSTOMNAME = '(empty)'

# -- values for proposal/sample/archival tool ----------------------------------

# path for script files
TCSPATH = '/data/scripts'

# paths for logfile archival
NICOSLOGPATH = '/data/log'
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
#       needscreation is true if the device needs a NicosCreate

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
