#  -*- coding: utf-8 -*-
# *****************************************************************************
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
# Module authors:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""TAS commands for NICOS."""

__version__ = "$Revision$"

from numpy import ndarray

from nicos import session
from nicos.core import Measurable, Moveable, Readable, UsageError
from nicos.scan import QScan
from nicos.commands import usercommand
from nicos.commands.scan import _infostr, ADDSCANHELP2


def _getQ(v, name):
    try:
        if len(v) == 4:
            return list(v)
        elif len(v) == 3:
            return [v[0], v[1], v[2], 0]
        else:
            raise TypeError
    except TypeError:
        raise UsageError('%s must be a sequence of (h, k, l) or (h, k, l, E)'
                         % name)

def _handleQScanArgs(args, kwargs, Q, dQ, scaninfo):
    preset, detlist, envlist, move, multistep = {}, [], None, [], []
    for arg in args:
        if isinstance(arg, str):
            scaninfo = arg + ' - ' + scaninfo
        elif isinstance(arg, (int, long, float)):
            preset['t'] = arg
        elif isinstance(arg, Measurable):
            detlist.append(arg)
        elif isinstance(arg, list):
            detlist.extend(arg)
        elif isinstance(arg, Readable):
            if envlist is None:
                envlist = []
            envlist.append(arg)
        else:
            raise UsageError('unsupported qscan argument: %r' % arg)
    for key, value in kwargs.iteritems():
        if key == 'h':
            Q[0] = value
        elif key == 'k':
            Q[1] = value
        elif key == 'l':
            Q[2] = value
        elif key == 'E':
            Q[3] = value
        elif key == 'dh':
            dQ[0] = value
        elif key == 'dk':
            dQ[1] = value
        elif key == 'dl':
            dQ[2] = value
        elif key == 'dE':
            dQ[3] = value
        elif key in session.devices and \
                 isinstance(session.devices[key], Moveable):
            if isinstance(value, list):
                if multistep and len(value) != len(multistep[-1][1]):
                    raise UsageError('all multi-step arguments must have the '
                                     'same length')
                multistep.append((session.devices[key], value))
            else:
                move.append((session.devices[key], value))
        else:
            # XXX this silently accepts wrong keys; restrict the possible keys?
            preset[key] = value
    return preset, scaninfo, detlist, envlist, move, multistep, Q, dQ


@usercommand
def qscan(Q, dQ, numsteps, *args, **kwargs):
    """Single-sided Q scan.

    The *Q* and *dQ* arguments can be lists of 3 or 4 components, or a `Q`
    object.
    """
    Q, dQ = _getQ(Q, 'Q'), _getQ(dQ, 'dQ')
    scanstr = _infostr('qscan', (Q, dQ, numsteps) + args, kwargs)
    preset, scaninfo, detlist, envlist, move, multistep, Q, dQ = \
            _handleQScanArgs(args, kwargs, Q, dQ, scanstr)
    if all(v == 0 for v in dQ) and numsteps > 1:
        raise UsageError('scanning with zero step width')
    values = [[(Q[0]+i*dQ[0], Q[1]+i*dQ[1], Q[2]+i*dQ[2], Q[3]+i*dQ[3])]
               for i in range(numsteps)]
    scan = QScan(values, move, multistep, detlist, envlist, preset, scaninfo)
    scan.run()


@usercommand
def qcscan(Q, dQ, numperside, *args, **kwargs):
    """Centered Q scan.

    The *Q* and *dQ* arguments can be lists of 3 or 4 components, or a `Q`
    object.
    """
    Q, dQ = _getQ(Q, 'Q'), _getQ(dQ, 'dQ')
    scanstr = _infostr('qcscan', (Q, dQ, numperside) + args, kwargs)
    preset, scaninfo, detlist, envlist, move, multistep, Q, dQ = \
            _handleQScanArgs(args, kwargs, Q, dQ, scanstr)
    if all(v == 0 for v in dQ) and numperside > 0:
        raise UsageError('scanning with zero step width')
    values = [[(Q[0]+i*dQ[0], Q[1]+i*dQ[1], Q[2]+i*dQ[2], Q[3]+i*dQ[3])]
               for i in range(-numperside, numperside+1)]
    scan = QScan(values, move, multistep, detlist, envlist, preset, scaninfo)
    scan.run()

qscan.__doc__  += ADDSCANHELP2.replace('scan(dev, ', 'qscan(Q, dQ, ')
qcscan.__doc__ += ADDSCANHELP2.replace('scan(dev, ', 'qcscan(Q, dQ, ')


class Q(ndarray):
    def __repr__(self):
        return str(self)

_Q = Q

@usercommand
def Q(*args, **kwds):
    """Create a Q-E vector that can be used for calculations.  Use:

    To create a Q vector (1, 0, 0) with energy transfer 0 or 5::

        q = Q(1)
        q = Q(1, 0, 0)
        q = Q(1, 0, 0, 5)
        q = Q(h=1, E=5)

    To create a Q vector from another Q vector, adjusting one or more entries::

        q2 = Q(q, h=2, k=1)
        q2 = Q(q, E=0)

    You can then use the Q-E vectors in scanning commands::

        qscan(q, q2, 5, t=10)
    """
    q = _Q(4)
    q[:] = 0.
    if not args:
        return q
    elif len(args) == 1:
        try:
            nlen = len(args[0])
        except TypeError:
            q[0] = args[0]
        else:
            for i in range(nlen):
                q[i] = args[0][i]
    elif len(args) > 4:
        raise UsageError('1 to 4 components are allowed')
    else:
        for i in range(len(args)):
            q[i] = args[i]
    if 'h' in kwds:
        q[0] = kwds['h']
    if 'k' in kwds:
        q[1] = kwds['k']
    if 'l' in kwds:
        q[2] = kwds['l']
    if 'E' in kwds:
        q[3] = kwds['E']
    return q
