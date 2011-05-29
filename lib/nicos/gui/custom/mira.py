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

"""MIRA customization for the GUI."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

# -- general configuration -----------------------------------------------------

# name of this custom configuration
CUSTOMNAME = 'MIRA'

# -- values for proposal/sample/archival tool ----------------------------------

# path for script files
TCSPATH = '/miracontrol'

# paths for logfile archival
NICOSLOGPATH = '/data/log'
DAEMONLOGPATH = '/data/log/daemon'

# general file finding function: return all data files from the specified
# proposal number and time span (given as (year, month, day) tuples)
def DATA_FILES(propnr, datefrom, dateuntil):
    import os

    years = [datefrom[0]]
    if dateuntil[0] != datefrom[0]:
        years.append(dateuntil[0])

    ret = []
    for year in years:
        lsd = os.listdir(os.path.join('/data', str(year), propnr))
        for fname in lsd:
            ret.append(os.path.join('/data', str(year), propnr, fname))
    return ret

# does the system support saved adjustments?
HAS_SAVED_ADJUSTS = True

# mutually exclusive instrument configurations
INSTRUMENTS = ['Mira1', 'Mira2']
# commands for init file to set one of the instrument configurations
INSTRUMENT_COMMANDS = ['SetInstrument(1)', 'SetInstrument(2)']
# nonexclusive optional add-ons
OPTIONS = ['MIEZE', 'PSD', 'Magnet', 'MuPAD', 'Polarized']

# values are: (instrument, options, defaultinwhichlist, needscreation)
# where instrument is an index into INSTRUMENTS, or -1 for "all"
#       options is a list of indices into OPTIONS, or empty if default
#       defaultinwhichlist determines if the device is on by default in the
#         "file header", "once for each point" and "continuous logging" lists
#       needscreation is true if the device needs a NicosCreate

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
    's1':    (1, (), (1, 0, 0), 0),

    # sample environment
    'T':     (-1, (), (0, 1, 1), 0),
    'Power': (-1, (), (0, 0, 0), 1),

    # options
    'psdet':   (-1, ('PSD',), (0, 0, 0), 1),

    'I':       (-1, ('Magnet',), (0, 1, 1), 0),

    'Flip1':   (-1, ('Polarized', 'MIEZE'), (1, 0, 0), 1),
    'Flip2':   (-1, ('Polarized', 'MIEZE'), (1, 0, 0), 1),
    'FlipperMira1in': (0, ('Polarized', 'MIEZE'), (1, 0, 0), 1),
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
    ('om', 'degrees'),
    ('phi', 'degrees'),
    ('sgx', 'degrees'),
    ('sgy', 'degrees'),
    ('stx', 'mm'),
    ('sty', 'mm'),
    ('sty', 'mm'),
    ('T', 'Kelvin'),
    ('I', 'Ampere'),
    ('Cor1', 'Ampere'),
    ('Cor2', 'Ampere'),
    ('Flip1', 'mm'),
    ('Flip2', 'mm'),
    ('mtt', 'degrees'),
    ('mth', 'degrees'),
]

# devices for ttscan
TTSCANDEVICES = [
    ('om', 'phi'),
    ('mth', 'mtt'),
]

# -- estimation functions ------------------------------------------------------

def _args_multiplied(*which):
    def analyzerfunc(analyzer, args, *ignored):
        t = 1
        for idx in which:
            t *= analyzer.const_eval(args[idx])
        analyzer.tick(0, 0, t)
    return analyzerfunc

def _do_det_preset(analyzer, args, *ignored):
    # catch preset default setting
    analyzer.locals['det__preset'] = analyzer.const_eval(args[0])

def _do_count(analyzer, args, *ignored):
    if not args:
        try:
            analyzer.tick(analyzer.locals['det__preset'])
        except KeyError:
            return
    else:
        analyzer.tick(analyzer.const_eval(args[0]))

def _do_psdcount(analyzer, args, *ignored):
    _do_count(analyzer, args, *ignored)
    # allow for the time the PSD needs to save the data file
    analyzer.tick(20)

def _do_sscan(analyzer, args, *ignored):
    start = analyzer.const_eval(args[1])
    step = analyzer.const_eval(args[2])
    numsteps = analyzer.const_eval(args[3])
    preset = analyzer.const_eval(args[4])
    count_time = preset * numsteps
    for i in range(numsteps):
        analyzer.do_move(args[0], start + i*step)
    analyzer.tick(count_time)

def _do_ttscan(analyzer, args, *ignored):
    start = analyzer.const_eval(args[2])
    step = analyzer.const_eval(args[3])
    numsteps = analyzer.const_eval(args[4])
    preset = analyzer.const_eval(args[5])
    count_time = preset * numsteps
    for i in range(numsteps):
        analyzer.do_move(args[0], start + i*step)
        analyzer.do_move(args[1], 2*start + i*2*step)
    analyzer.tick(count_time)

def _do_cscan(analyzer, args, *ignored):
    center = analyzer.const_eval(args[1])
    step = analyzer.const_eval(args[2])
    numperside = analyzer.const_eval(args[3])
    start = center - step * numperside
    preset = analyzer.const_eval(args[4])
    count_time = preset * (numperside*2 + 1)
    for i in range(numperside * 2+1):
        analyzer.do_move(args[0], start + i*step)
    analyzer.tick(count_time)

def _do_qcscan(analyzer, args, call, *ignored):
    argnames = ['Qh', 'Qk', 'Ql', 'ny', 'dQh', 'dQk', 'dQl', 'dny',
                'numsteps', 'SC', 'preset', 'plot']
    argdefaults = [0., 0., 0., 0., 0., 0., 0., 0., 1, 2.662, None, None]
    args = analyzer.parse_args('qcscan', call, argnames, argdefaults)[0]
    if args['preset'] is None:
        args['preset'] = analyzer.locals.get('det__preset', 1)
    analyzer.tick((analyzer.const_eval(args['numsteps']) * 2 + 1) *
                  analyzer.const_eval(args['preset']))

def _do_qsscan(analyzer, args, call, *ignored):
    argnames = ['Qh', 'Qk', 'Ql', 'ny', 'dQh', 'dQk', 'dQl', 'dny',
                'numsteps', 'SC', 'preset', 'plot']
    argdefaults = [0., 0., 0., 0., 0., 0., 0., 0., 1, 2.662, None, None]
    args = analyzer.parse_args('qsscan', call, argnames, argdefaults)[0]
    if args['preset'] is None:
        args['preset'] = analyzer.locals.get('det__preset', 1)
    analyzer.tick(analyzer.const_eval(args['numsteps']) *
                  analyzer.const_eval(args['preset']))

def _do_qlscan(analyzer, args, call, *ignored):
    argnames = ['Qh', 'Qk', 'Ql', 'ny', 'dq', 'dny',
                'numsteps', 'SC', 'preset', 'plot']
    argdefaults = [0., 0., 0., 0., 0., 0., 1, 2.662, None, None]
    args = analyzer.parse_args('qlscan', call, argnames, argdefaults)[0]
    if args['preset'] is None:
        args['preset'] = analyzer.locals.get('det__preset', 1)
    analyzer.tick((analyzer.const_eval(args['numsteps']) * 2 + 1) *
                  analyzer.const_eval(args['preset']))

def _do_qtscan(analyzer, args, call, *ignored):
    argnames = ['Qh', 'Qk', 'Ql', 'ny', 'dq', 'dny',
                'numsteps', 'SC', 'preset', 'plot']
    argdefaults = [0., 0., 0., 0., 0., 0., 1, 2.662, None, None]
    args = analyzer.parse_args('qtscan', call, argnames, argdefaults)[0]
    if args['preset'] is None:
        args['preset'] = analyzer.locals.get('det__preset', 1)
    analyzer.tick((analyzer.const_eval(args['numsteps']) * 2 + 1) *
                  analyzer.const_eval(args['preset']))

#def _do_qrscan(analyzer, args, *ignored):
#    pass

# MIEZE
def _mieze_args_multiplied(*which):
    def dofunc(analyzer, args, *ignored):
        t = 1
        for idx in which:
            t *= analyzer.const_eval(args[idx])
        # MIEZE times
        mtimes = analyzer.const_eval(args[0])
        if mtimes is None or isinstance(mtimes, basestring):
            analyzer.tick(t)
        else:
            analyzer.tick(t * len(mtimes))
    return dofunc

def _do_msscan(analyzer, args, *ignored):
    mtimes = analyzer.const_eval(args[0])
    if mtimes is None or isinstance(mtimes, basestring):
        numtimes = 1
    else:
        numtimes = len(mtimes)
    start = analyzer.const_eval(args[2])
    step = analyzer.const_eval(args[3])
    numsteps = analyzer.const_eval(args[4])
    preset = analyzer.const_eval(args[5])
    count_time = numtimes * preset * numsteps
    for i in range(numsteps):
        analyzer.do_move(args[1], start + i*step)
    analyzer.tick(count_time)

def _do_mttscan(analyzer, args, *ignored):
    mtimes = analyzer.const_eval(args[0])
    if mtimes is None or isinstance(mtimes, basestring):
        numtimes = 1
    else:
        numtimes = len(mtimes)
    start = analyzer.const_eval(args[3])
    step = analyzer.const_eval(args[4])
    numsteps = analyzer.const_eval(args[5])
    preset = analyzer.const_eval(args[6])
    count_time = numtimes * preset * numsteps
    for i in range(numsteps):
        analyzer.do_move(args[1], start + i*step)
        analyzer.do_move(args[1], 2*start + i*2*step)
    analyzer.tick(count_time)

def _do_mcscan(analyzer, args, *ignored):
    mtimes = analyzer.const_eval(args[0])
    if mtimes is None or isinstance(mtimes, basestring):
        numtimes = 1
    else:
        numtimes = len(mtimes)
    center = analyzer.const_eval(args[2])
    step = analyzer.const_eval(args[3])
    numperside = analyzer.const_eval(args[4])
    start = center - step * numperside
    preset = analyzer.const_eval(args[5])
    count_time = numtimes * preset * (numperside*2 + 1)
    for i in range(numperside*2 + 1):
        analyzer.do_move(args[1], start + i*step)
    analyzer.tick(count_time)

def _do_mrawscan(analyzer, args, *ignored):
    import _ast
    mtimes = analyzer.const_eval(args[0])
    if mtimes is None or isinstance(mtimes, basestring):
        numtimes = 1
    else:
        numtimes = len(mtimes)
    if not isinstance(args[1], _ast.List):
        # raise NotConst
        analyzer.const_eval(None)
    stagelist = args[1].elts
    pointlists = analyzer.const_eval(args[2])
    npoints = len(pointlists[0])
    preset = analyzer.const_eval(args[3])
    count_time = npoints * preset * numtimes
    for stage, values in zip(stagelist, pointlists):
        for value in values:
            analyzer.do_move(stage, value)
    analyzer.tick(count_time)

def _do_mupdown(analyzer, args, *ignored):
    preset = analyzer.const_eval(args[0])
    analyzer.tick(preset * 2)

def _do_twodscan(analyzer, args, *ignored):
    dev1 = args[0]
    start1 = analyzer.const_eval(args[1])
    step1 = analyzer.const_eval(args[2])
    num1 = analyzer.const_eval(args[3])
    dev2 = args[4]
    start2 = analyzer.const_eval(args[5])
    step2 = analyzer.const_eval(args[6])
    num2 = analyzer.const_eval(args[7])
    preset = analyzer.const_eval(args[9])
    countfunc = args[8]
    # up/down scans take twice the time, try to cover that
    funcname = getattr(countfunc, 'id', None)
    if funcname == 'mupdown_r':
        preset *= 2
    npoints = analyzer.const_eval(args[3]) * analyzer.const_eval(args[7])
    count_time = npoints * preset
    for i1 in range(num1):
        analyzer.do_move(dev1, start1 + i1*step1)
        for i2 in range(num2):
            if i1 % 2 == 0:
                analyzer.do_move(dev2, start2 + i2*step2)
            else:
                analyzer.do_move(dev2, start2 + (num2-i2-1)*step2)
    analyzer.tick(count_time)

def _do_move(analyzer, args, *ignored):
    devarg = args[0]
    pos = analyzer.const_eval(args[1])
    analyzer.do_move(devarg, pos)

def _do_nothing(analyzer, args, *ignored):
    pass

ANALYZERS = {
    'sleep': _args_multiplied(0),
    'longsleep': _args_multiplied(0),
    'time.sleep': _args_multiplied(0),
    'det._preset': _do_det_preset,
    'count': _do_count,
    'mcount': _do_count,
    'psdcount': _do_psdcount,
    'sscan': _do_sscan,
    'ttscan': _do_ttscan,
    'cscan': _do_cscan,
    'mcheck': _mieze_args_multiplied(0),
    'msingle': _mieze_args_multiplied(1),
    'msscan': _do_msscan,
    'mttscan': _do_mttscan,
    'mcscan': _do_mcscan,
    'mrawscan': _do_mrawscan,
    'mupdown': _do_mupdown,
    'twodscan': _do_twodscan,
    'move': _do_move,
    'maw': _do_move,
    'switch': _do_move,
    'MiezeDataSet': _do_nothing,
    'qcscan': _do_qcscan,
    'qsscan': _do_qsscan,
    'qtscan': _do_qtscan,
    'qlscan': _do_qlscan,
    #'qrscan': _do_qrscan,
    # should be checked at some point
    'wait': _do_nothing,
    'read': _do_nothing,
    'stop': _do_nothing,
    'status': _do_nothing,
    'get': _do_nothing,
    'set': _do_nothing,
    'reset': _do_nothing,
    'adjust': _do_nothing,
    'center': _do_nothing,
    'fix': _do_nothing,
    'unfix': _do_nothing,
    'showFixed': _do_nothing,
    'countmode': _do_nothing,
    'mplot': _do_nothing,
    'sendmail': _do_nothing,
    # init file commands
    'DataBox.newexperiment': _do_nothing,
    'DataBox.setSampleInfo': _do_nothing,
    'DataBox.setSampleDetectorDistance': _do_nothing,
    'SetInstrument': _do_nothing,
    'SetMailReceivers': _do_nothing,
    'SetSMSReceivers': _do_nothing,
    'NicmFactory': _do_nothing,
    'DataBox.clearAdjusts': _do_nothing,
    'DataBox.loadAdjusts': _do_nothing,
    # general builtins
    'sum': _do_nothing,
    'int': _do_nothing,
    'float': _do_nothing,
    'abs': _do_nothing,
    'str': _do_nothing,
    'math.sqrt': _do_nothing,
    'math.acos': _do_nothing,
    'math.cos': _do_nothing,
    'math.asin': _do_nothing,
    'math.sin': _do_nothing,
}

def _do_move_t(analyzer, diff):
    if abs(diff) <= 0.5:
        analyzer.tick(0, 150)
    analyzer.tick(0, 500)

def _simple_move(speed, const):
    def _do(analyzer, diff):
        analyzer.tick(0, const + abs(diff) * speed)
    return _do

MOVE_ANALYZERS = {
    'T': _do_move_t,
    'I': _simple_move(1, 0.5),
    'dtz': _simple_move(0.1, 0.2),
    'dty': _simple_move(1, 0.2),
    'sgy': _simple_move(74., 4),
    'stz': _simple_move(3.3, 6),
}

# -- maintenance commands ------------------------------------------------------

MAINT_COMMANDS = [
    ('Restart TACO server for RS232/mira1',
     'ssh maint@mira1 sudo /etc/init.d/taco-server-rs232 restart'),
    ('Restart TACO server for RS485/mira1',
     'ssh maint@mira1 sudo /etc/init.d/taco-server-rs485 restart'),
    ('Restart TACO server for LakeShore',
     'ssh maint@mira1 sudo /etc/init.d/taco-server-lakeshore340 restart'),
    ('Restart TACO server for Phytron',
     'ssh maint@mira1 sudo /etc/init.d/taco-server-phytronixe restart'),
    ('Restart TACO server for FRM counter',
     'ssh maint@mira1 sudo /etc/init.d/taco-server-frmcounter restart'),
    ('Restart TACO server for ZUPs',
     'ssh maint@mira1 sudo /etc/init.d/taco-server-zup restart'),
    ('Restart TACO server for IPC encoder',
     'ssh maint@mira1 sudo /etc/init.d/taco-server-ipcencoder restart'),

    ('Restart TACO server for RS232/mira4',
     'ssh maint@mira4 sudo /etc/init.d/taco-server-rs232 restart'),
    ('Restart TACO server for network/mira4',
     'ssh maint@mira4 sudo /etc/init.d/taco-server-network restart'),
    ('Restart TACO server for HPE power supplies',
     'ssh maint@mira4 sudo /etc/init.d/taco-server-hpe3631a restart'),
    ('Restart TACO server for NTN (FUG)',
     'ssh maint@mira4 sudo /etc/init.d/taco-server-ntn14000m restart'),
    ('Restart TACO server for Heinzinger',
     'ssh maint@mira4 sudo /etc/init.d/taco-server-heinzingerptn3p restart'),
    ('Restart TACO server for Tektronix',
     'ssh maint@mira4 sudo /etc/init.d/taco-server-tektronixtds restart'),
    ('Restart TACO server for Agilent frequency generators',
     'ssh maint@mira4 sudo /etc/init.d/taco-server-hp33250a restart'),
    ('Restart TACO server for C-Boxes',
     'ssh maint@mira4 sudo /etc/init.d/taco-server-pci2032 restart'),
    ('Restart TACO server for TMCA counter',
     'ssh maint@mira4 sudo /etc/init.d/taco-server-tmca restart'),
]

# ------------------------------------------------------------------------------
