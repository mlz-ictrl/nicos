#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

"""
Created on 06.06.2011

@author: pedersen
"""

__version__ = "$Revision$"

#from nicos import session
#from nicos.core.scan import Scan, TimeScan, ContinuousScan, ManualScan
#from nicos.core import Device, Measurable, Moveable, Readable
from nicos.core import UsageError
from nicos.commands import usercommand

from nicos.resi import residevice

@usercommand
def measuredataset(dev,**kw):
    ''' Mesasure a single crystal dataset

    dev: residevice instance [req]

    use one of:

    dataset: array of reflections to measure

    thmin: min 2-theta
    thmax: max 2-theta

    dmin: min d-spacing
    dmax: max d-spacing

    optional:
    stime: scan time
    delta: scan width
    step: step width

    '''
    print 'measure',kw
    if not kw:
        raise UsageError('at least two arguments are required')

    if kw.has_key('dataset'):
        ds = kw['dataset']
        del kw['dataset']
    elif kw.has_key('thmin'):
        if not kw.has_key('thmax'):
            raise UsageError('thmin and thmax need to be given both')
        else:
            ds = dev._hardware.getScanDataset(thmax=kw['thmax'],thmin=kw['thmin'])
            del kw['thmax']
            del kw['thmin']
    elif kw.has_key('thmax'):
        if not kw.has_key('thmin'):
            raise UsageError('thmin and thmax need to be given both')
        else:
            ds = dev._hardware.getScanDataset(thmax=kw['thmax'],thmin=kw['thmin'])
            del kw['thmax']
            del kw['thmin']
    elif kw.has_key('dmin'):
        if not kw.has_key('dmax'):
            raise UsageError('dmin and dmax need to be given both')
        else:
            ds = dev._hardware.getScanDataset(dmax=kw['dmax'],dmin=kw['dmin'])
            del kw['dmax']
            del kw['dmin']
    elif kw.has_key('dmax'):
        if not kw.has_key('dmin'):
            raise UsageError('dmin and dmax need to be given both')
        else:
            ds = dev._hardware.getScanDataset(dmax=kw['dmax'],dmin=kw['dmin'])
            del kw['dmax']
            del kw['dmin']

    if not isinstance(dev,residevice.ResiDevice):
        raise UsageError('This command only works with the resi device')

    dev._hardware.DoScan(ds=ds,**kw)
