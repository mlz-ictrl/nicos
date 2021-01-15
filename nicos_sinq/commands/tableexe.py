#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
# Module authors:
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************
"""
  At SINQ, we use batch files in the form of speadsheet tables in csv format.
  The workflow is such that the instrument scientist prepares the header,
  the user fills in er data and then executes the spreadsheet. For editing,
  a normal spreadsheet program is used and the table then exported in csv
  format.

  The header row of the table has a special meaning: it defines how the
  following table lines are expressed through the column names. Supported are:
  - device names, this causes the device to be driven to the value given in
    later table rows
  - NICOS parameter names. This causes the corresponding NICOS parameter
    to be set
  - timer or monitor are special names which cause a count() command to
    be called with either a timer or monitor preset
  - command is another special name which causes the command specified
    as data to be executed verbatim.

  Device driving and parameter setting commands are executed first, then
  monitor, timer or command. Of these three only one can be present in
  any given row.

  The way this is implemented is that the csv file is cross compiled to a NICOS
  python file which then is executed through the normal script running commands
  of NICOS.
"""

import csv
import os
from os import path

from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.commands.device import _basemove, _wait_hook
from nicos.commands.output import printinfo
from nicos.core import UsageError
from nicos.services.daemon.utils import parseScript


def _csvfilename(filename):
    fn = filename
    if not path.isabs(fn):
        fn = path.normpath(path.join(session.experiment.scriptpath, fn))
    # does the file exist?
    if fn.endswith(('.csv',)) and path.isfile(fn):
        return fn
    # can I find it when I add an extension?
    if path.isfile(fn + '.csv'):
        return fn + '.csv'


@usercommand
@helparglist('CSV file to run')
def tableexe(csvfile):
    """
     Tableexe executes an execution table provided
     as a CSV file
     :param csvfile: The csv file to run
     """
    fname = _csvfilename(csvfile)
    if not fname or \
            (not path.isfile(fname) and os.access(fname, os.R_OK)):
        raise UsageError('The file %r does not exist or is not readable'
                         % fname)
    with open(fname, 'r') as fin:
        csv_data = csv.reader(fin, delimiter=',')
        # Analyse header
        devlist = []
        parlist = []
        comlist = []
        strlist = []
        comnames = ['timer', 'monitor', 'command']
        header = next(csv_data)
        for col_name in header:
            if not col_name:
                continue
            if col_name in comnames:
                comlist.append(col_name)
                continue
            if col_name in session.devices:
                dev = session.getDevice(col_name)
                if isinstance(dev.read(), str):
                    strlist.append(col_name)
                devlist.append(col_name)
                continue
            try:
                devname, par = col_name.split('.')
                dev = session.getDevice(devname)
                if par in dev.parameters:
                    parlist.append(col_name)
                    if isinstance(dev.parameters[par], str):
                        strlist.append(col_name)
                else:
                    raise UsageError('%s has no parameter %s' % (devname, par))
            except Exception:
                raise UsageError(
                    'Unrecognised column name %s' % col_name) from None

        # Actually execute the CSV data
        idx = 0
        printinfo('Executing CSV from %s' % csvfile)
        for data in csv_data:
            if not data:
                continue
            idx = idx + 1
            dev_value = []
            commands = []
            printinfo('Working line %d of %s'
                      % (idx, os.path.basename(csvfile)))
            for col_name, value in zip(header, data):
                if col_name in devlist:
                    dev_value.append(value)
                    continue
                if col_name in parlist:
                    lv = col_name.split('.')
                    dev = session.getDevice(lv[0])
                    setattr(dev, lv[1], value)
                    continue
                if col_name == 'timer':
                    commands.append('count(t=%s)' % value)
                elif col_name == 'monitor':
                    commands.append('count(m=%s)' % value)
                else:
                    commands.append(value)
            dev_poslist = ()
            for dev, value in zip(devlist, dev_value):
                dev_poslist += (dev,)
                if dev in strlist:
                    dev_poslist += (value,)
                else:
                    dev_poslist += (float(value),)
            _basemove(dev_poslist, waithook=_wait_hook)
            for com in commands:
                if com:
                    code, _ = parseScript(com)
                    for c in code:
                        exec(c, session.namespace)
            session.breakpoint(2)
