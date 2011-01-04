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

"""PUMA customization for the GUI."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

# -- general configuration -----------------------------------------------------

# name of this custom configuration
CUSTOMNAME = 'PUMA'

# -- values for proposal/sample/archival tool ----------------------------------

# path for tcs files
TCSPATH = '/pumacontrol/scripts'

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
INSTRUMENTS = ['PUMA']
# commands for init file to set one of the instrument configurations
INSTRUMENT_COMMANDS = ['']
# nonexclusive optional add-ons
OPTIONS = ['MIEZE', 'PSD', 'Magnet', 'MuPAD', 'Polarized']

# values are: (instrument, options, defaultinwhichlist, needscreation)
# where instrument is an index into INSTRUMENTS, or -1 for "all"
#       options is a list of indices into OPTIONS, or empty if default
#       defaultinwhichlist determines if the device is on by default in the
#         "file header", "once for each point" and "continuous logging" lists
#       needscreation is true if the device needs a NicmCreate

DEVICES = {
    # sample table
    'om':    (-1, (), (1, 0, 0), 0),
    'phi':   (-1, (), (1, 0, 0), 0),
    'stx':   (-1, (), (1, 0, 0), 0),
    'sty':   (-1, (), (1, 0, 0), 0),
    'stz':   (-1, (), (1, 0, 0), 0),
    'sgx':   (-1, (), (1, 0, 0), 0),
    'sgy':   (-1, (), (1, 0, 0), 0),
    #'s3':    (-1, (), (1, 0, 0), 0),
    's4':    (-1, (), (1, 0, 0), 0),

    # mira1 monochromator
    'lam':   (0, (), (1, 0, 0), 0),
    'mth':   (0, (), (1, 0, 0), 0),
    'mtt':   (0, (), (1, 0, 0), 0),
    'mtx':   (0, (), (1, 0, 0), 0),
    'mty':   (0, (), (1, 0, 0), 0),
    'mgx':   (0, (), (1, 0, 0), 0),
    's1':    (0, (), (1, 0, 0), 0),
    's2':    (0, (), (1, 0, 0), 0),
    'FOL':   (0, (), (1, 0, 0), 0),
    'FOLin': (0, (), (1, 0, 0), 0),

    # mira2 monochromator
    'lam2':  (1, (), (1, 0, 0), 0),
    'm2th':  (1, (), (1, 0, 0), 0),
    'm2tt':  (1, (), (1, 0, 0), 0),
    'm2tx':  (1, (), (1, 0, 0), 0),
    'm2ty':  (1, (), (1, 0, 0), 0),
    'm2gx':  (1, (), (1, 0, 0), 0),
    'm2gy':  (1, (), (1, 0, 0), 0),

    # sample environment
    'T':     (-1, (), (0, 1, 1), 0),
    'Power': (-1, (), (0, 0, 0), 1),

    # options
    'psdet':   (-1, ('PSD',), (0, 0, 0), 1),

    'I':       (-1, ('Magnet',), (0, 1, 1), 0),

    'Flip1':   (-1, ('Polarized', 'MIEZE'), (1, 0, 0), 1),
    'Flip2':   (-1, ('Polarized', 'MIEZE'), (1, 0, 0), 1),
    'Flipper1in': (-1, ('Polarized', 'MIEZE'), (1, 0, 0), 1),
    'Cor1':    (-1, ('Polarized', 'MIEZE'), (1, 0, 0), 1),
    'Cor2':    (-1, ('Polarized', 'MIEZE'), (1, 0, 0), 1),

    'Cbox1':   (-1, ('MIEZE', 'Polarized'), (1, 0, 0), 1),
    'Cbox2':   (-1, ('MIEZE', 'Polarized'), (1, 0, 0), 1),

    'dc1':     (-1, ('MIEZE',), (0, 1, 0), 1),
    'dc2':     (-1, ('MIEZE',), (0, 1, 0), 1),
    'amp1':    (-1, ('MIEZE',), (0, 1, 0), 1),
    'amp2':    (-1, ('MIEZE',), (0, 1, 0), 1),
    'amp3':    (-1, ('MIEZE',), (0, 1, 0), 1),
    'amp4':    (-1, ('MIEZE',), (0, 1, 0), 1),
    'freq1':   (-1, ('MIEZE',), (0, 1, 0), 1),
    'freq2':   (-1, ('MIEZE',), (0, 1, 0), 1),
    'freq3':   (-1, ('MIEZE',), (0, 1, 0), 1),
    'freq4':   (-1, ('MIEZE',), (0, 1, 0), 1),
    'dc3p6':   (-1, ('MIEZE',), (1, 0, 0), 1),
    'dc3p25':  (-1, ('MIEZE',), (1, 0, 0), 1),
    'dc3n25':  (-1, ('MIEZE',), (1, 0, 0), 1),
    'dc4p6':   (-1, ('MIEZE',), (1, 0, 0), 1),
    'dc4p25':  (-1, ('MIEZE',), (1, 0, 0), 1),
    'dc4n25':  (-1, ('MIEZE',), (1, 0, 0), 1),
    'mult':    (-1, ('MIEZE',), (0, 0, 0), 1),
    'mieze':   (-1, ('MIEZE',), (0, 0, 0), 1),

    'muccin':  (-1, ('MuPAD',), (1, 0, 0), 1),
    'muccout': (-1, ('MuPAD',), (1, 0, 0), 1),
    'muinput': (-1, ('MuPAD',), (1, 0, 0), 1),
    'muoutput':(-1, ('MuPAD',), (1, 0, 0), 1),

}

# from tas_globals.py
TASOPMODELIST = [
    ('CKF', 'const. kf'),
    ('CKI', 'const. ki'),
    ('CPSI', 'const. psi'),
    ('CPHI', 'const. phi'),
    ('BEF', 'Beryllium filter'),
    ('PWD', 'powder on sample table'),
    ('DIFF', 'without analyser'),
]

ETRANSFERUNITS = ['THz', 'meV']

# -- values for scan input -----------------------------------------------------

# devices for sscan and cscan: name and unit
SCANDEVICES = [
    ('ki', 'A-1'),
    ('kf', 'A-1'),
    ('dmo', 'deg.'),
    ('phi', 'deg.'),
    ('psi', 'deg.'),
    ('sgx', 'deg.'),
    ('sgy', 'deg.'),
    ('stx', 'mm'),
    ('sty', 'mm'),
    ('stz', 'mm'),
    ('slit1', 'mm'),
    ('slit2', 'mm'),
    ('tsa', 'Kelvin'),
]

# devices for ttscan
TTSCANDEVICES = [
    ('psi', 'phi'),
    ('mth', 'mtt'),
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
