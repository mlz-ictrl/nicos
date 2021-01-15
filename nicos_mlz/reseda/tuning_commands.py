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
#   Christian Franz  <christian.franz@frm2.tum.de>
#
# *****************************************************************************

"""Module for RESEDA tunewavetable specific commands."""

import csv
from os import path

from nicos import session
from nicos.commands import usercommand
from nicos.commands.output import printerror, printinfo

__all__ = ['ExportTuning', 'ImportTuning']


@usercommand
def ExportTuning(mode, wavelength, filename='tuning'):
    """Export tuning for *mode* and *wavelength* to a CSV file.

    Mode can be "nrse" or "mieze".
    """
    echotime = session.getDevice('echotime')
    exp = session.getDevice('Exp')

    # get the right table
    try:
        tables = echotime.tables[mode]
    except KeyError:
        printerror('Need a valid mode (mieze or nrse)')
        return
    try:
        table = tables[wavelength]
    except KeyError:
        printerror('No table for this wavelength (available: %s)' %
                   ', '.join(map(str, tables)))

    # build list of devices
    it = iter(table.values())
    devices = sorted(it.next())
    for otherdevs in it:
        devices.extend(set(otherdevs) - set(devices))

    # export to CSV
    filename = path.join(exp.dataroot, filename + '_%s_%sA.csv' % (mode, wavelength))
    printinfo('Exporting to %s' % filename)
    if path.exists(filename):
        printerror('File already exists. Please select another name.')
        return
    with open(filename, 'w') as fp:
        writer = csv.writer(fp)
        writer.writerow(['echotime'] + devices)
        for (etime, devs) in table.items():
            writer.writerow([repr(etime)] + [repr(devs.get(d)) for d in devices])
    printinfo('Done.')


def try_float(d):
    try:
        return float(d.replace(',', '.'))
    except ValueError:
        return d


@usercommand
def ImportTuning(mode, wavelength, filename='tuning'):
    """Import tuning for *mode* and *wavelength* from a CSV file.

    Mode can be "nrse" or "mieze".
    """
    echotime = session.getDevice('echotime')
    exp = session.getDevice('Exp')

    filename = path.join(exp.dataroot, filename + '_%s_%sA.csv' % (mode, wavelength))
    printinfo('Importing from %s' % filename)
    if not path.exists(filename):
        printerror('File does not exist. Please select another name.')
        return
    newtable = {}
    with open(filename, 'r') as fp:
        reader = iter(csv.reader(fp))
        headers = reader.next()
        if headers[0] != 'echotime':
            printerror('This does not appear to be a tuning table.')
            return
        devices = headers[1:]
        for row in reader:
            etime = try_float(row[0])
            devs = {}
            for (d, val) in zip(devices, row[1:]):
                if val != 'None':
                    devs[d] = try_float(val)
            newtable[etime] = devs
    echotime.setTable(mode, wavelength, newtable)
    printinfo('Done.')
