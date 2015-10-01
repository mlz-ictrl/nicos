#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

"""Module with specific commands for POLI."""

from nicos import session
from nicos.commands import usercommand, helparglist
from nicos.commands.device import maw
from nicos.commands.scan import cscan, contscan
from nicos.commands.analyze import center_of_mass, gauss
from nicos.commands.output import printinfo
from nicos.core import Moveable, UsageError, NicosError
from nicos.pycompat import number_types


@usercommand
@helparglist('device1, device2, ..., [rounds=N], [steps=N], [steps_device1=N],'
             ' [step=stepsize], [step_device1=stepsize], [fit="func"], '
             '[cont=True], [convergence=C], [preset]')
def centerpeak(*args, **kwargs):
    """Center a peak with multiple scans over multiple devices.

    This does repeated scans of all devices to iteratively center a peak until
    the peak center does not shift anymore.  Starting position is the current
    position of all devices.

    Non-keyword arguments are devices to scan over. At least one is required.

    Supported keyword arguments are:

    * ``rounds`` - maximum number of rounds (a round is one scan per device).
      The default is 5.
    * ``steps`` - number of steps per side for each scan. The default is 15.
    * ``steps_devname`` - special number of steps per side for this device.
    * ``step`` - step size for each scan. The default is 0.1.
    * ``step_devname`` - special step size for this device.
    * ``convergence`` - maximum delta of peak center between two scans of a
      device, in units of the scan step size. The default is 0.5.
    * ``fit`` - fit function to use for determining peak center, see below.
    * ``cont`` - True/False whether to use continuous scans. Default is false.
    * all further keyword arguments (like ``t=1``) are used as detector presets.

    Examples:

    # default scan without special options, count 2 seconds
    >>> centerpeak(omega, twotheta, 2)
    # scan with device-specific step size and number of steps
    >>> centerpeak(omega, twotheta, step_omega=0.05, steps_omega=20, t=1)
    # allow a large number of rounds with very small convergence window
    # (1/5 of step size)
    >>> centerpeak(omega, twotheta, rounds=10, convergence=0.2, t=1)
    # center using Gaussian peak fits
    >>> centerpeak(omega, twotheta, fit='gauss', t=1)

    Fit functions:

    * ``'center_of_mass'``: default, works for any peak shape
    * ``'gauss'``: symmetric Gaussian
    """
    nrounds = 5
    devices = []
    defsteps = 15
    nsteps = {}
    defstepsize = 0.1
    stepsizes = {}
    preset = {}
    fit = 'center_of_mass'
    allowed_fit = set(['center_of_mass', 'gauss'])
    continuous = False
    convergence = 0.5
    for devname in args:
        if isinstance(devname, number_types):
            preset['t'] = devname
        else:
            devices.append(session.getDevice(devname, Moveable))
    if not devices:
        raise UsageError('need at least one device to scan over')
    for kw, value in kwargs.items():
        if kw == 'rounds':
            nrounds = value
        elif kw == 'fit':
            if value not in allowed_fit:
                raise UsageError('fit function %s is not allowed' % value)
            fit = value
        elif kw == 'convergence':
            convergence = value
        elif kw == 'steps':
            defsteps = value
        elif kw == 'step':
            defstepsize = value
        elif kw == 'cont':
            continuous = bool(value)
        elif kw.startswith('step_'):
            dev = session.getDevice(kw[5:], Moveable)
            if dev not in devices:
                raise UsageError('device %s not in list of devices to scan' %
                                 dev)
            stepsizes[dev] = value
        elif kw.startswith('steps_'):
            dev = session.getDevice(kw[6:], Moveable)
            if dev not in devices:
                raise UsageError('device %s not in list of devices to scan' %
                                 dev)
            nsteps[dev] = value
        else:
            preset[kw] = value
    for dev in devices:
        if dev not in stepsizes:
            stepsizes[dev] = defstepsize
        if dev not in nsteps:
            nsteps[dev] = defsteps

    # main loop
    lastround = dict((dev, dev.read()) for dev in devices)
    for i in range(nrounds):
        printinfo('Round %d of %d' % (i + 1, nrounds))
        printinfo('*' * 100)
        # results of last round
        thisround = {}
        for dev in devices:
            center = lastround[dev]
            if continuous:
                contscan(dev, center - nsteps[dev] * stepsizes[dev],
                         center + nsteps[dev] * stepsizes[dev],
                         speed=stepsizes[dev] / preset.get('t', 1),
                         timedelta=preset.get('t', 1))
            else:
                cscan(dev, center, stepsizes[dev], nsteps[dev], *devices,
                      **preset)
            if fit == 'center_of_mass':
                thisround[dev] = center_of_mass()
            elif fit == 'gauss':
                params, _ = gauss()
                minvalue = center - abs(stepsizes[dev] * nsteps[dev])
                maxvalue = center + abs(stepsizes[dev] * nsteps[dev])
                if params is None:
                    maw(dev, center)
                    raise NicosError('no Gaussian fit found in this scan')
                fit_center = params[0]
                if not minvalue <= fit_center <= maxvalue:
                    maw(dev, center)
                    raise NicosError('Gaussian fit center outside scanning area')
                thisround[dev] = fit_center
            maw(dev, thisround[dev])
        printinfo('*' * 100)
        again = False
        for dev in devices:
            diff = abs(lastround[dev] - thisround[dev])
            printinfo('%-10s center: %8.6g -> %8.6g (delta %8.6g)' %
                      (dev, lastround[dev], thisround[dev], diff))
            if diff > convergence * stepsizes[dev]:
                if i == nrounds - 1:
                    printinfo('=> would need another round, but command '
                              'limited to %d rounds' % nrounds)
                else:
                    printinfo('=> needs another round')
                again = True
        if not again:
            printinfo('=> found convergence on peak:')
            for dev in devices:
                printinfo('%-10s : %s' % (dev, dev.format(dev())))
            return
        lastround = thisround
