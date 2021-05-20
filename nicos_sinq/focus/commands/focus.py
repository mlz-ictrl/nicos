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

import numpy as np

from nicos import session
from nicos.commands import helparglist, parallel_safe, usercommand
from nicos.commands.device import maw
from nicos.core.errors import ConfigurationError


@usercommand
@helparglist('start,step,count')
def UpdateTimeBinning(start, step, count):
    """
    Updates all available HM's with a new time binning
    """
    # FOCUS uses one shared array for TOF configuration
    hms = ['middle', 'upper', 'lower', 'f2d']
    # Keep a copy of delay for writing to data file
    dl = session.getDevice('delay')
    maw(dl, start)
    # First set the delay time to all MDIF's
    dt = start % 200000
    for hm in hms:
        try:
            mdif = session.getDevice('mdif_' + hm)
            mdif.execute('DT %d\r' % dt)
        except ConfigurationError:
            pass
    tof = session.getDevice('hm_tof_array')
    # For configuration we start at 0
    tof.updateTimeBins(0, step, count)
    # Now configure all, possibly four HM
    for hm in hms:
        try:
            cfg = session.getDevice(hm + '_configurator')
            cfg.updateConfig()
        except ConfigurationError:
            # Missing HM's are normal
            pass
    # Now make sure that the user sees the right thing
    tof.updateTimeBins(start, step, count)


@usercommand
@parallel_safe
def ShowTimeBinning():
    """
    Shows the currently configured time binning
    """
    # Get the configurator device
    arr = session.getDevice('hm_tof_array')
    count = len(arr.data)
    step = arr.data[1] - arr.data[0]
    start = arr.data[0]
    session.log.info('Time Binning: start: %d, step %d, count = %d',
                     start, step, count)


@usercommand
def LoadThetaArrays():
    """
    Loads the theta values from focusmerge.dat into the arrays for use in
    NeXus file writing.
    """
    with open('nicos_sinq/focus/focusmerge.dat') as fin:
        fin.readline()  # skip first
        # First: the merged data theta
        length = int(fin.readline())
        data = np.zeros((length,), dtype='float32')
        for i in range(length):
            line = fin.readline()
            ld = line.split()
            data[i] = float(ld[1])
        conf = session.getDevice('merged_theta')
        conf.setData([length], data)
        fin.readline()  # Skip another line
        # Second: upper bank theta
        length = int(fin.readline())
        data = np.zeros((length,), dtype='float32')
        for i in range(length):
            data[i] = float(fin.readline())
        conf = session.getDevice('upper_theta')
        conf.setData([length], data)
        fin.readline()  # Skip another line
        # Third: middle bank theta
        length = int(fin.readline())
        data = np.zeros((length,), dtype='float32')
        for i in range(length):
            data[i] = float(fin.readline())
        conf = session.getDevice('middle_theta')
        conf.setData([length], data)
        fin.readline()  # Skip another line
        # Last: lower bank theta
        length = int(fin.readline())
        data = np.zeros((length,), dtype='float32')
        for i in range(length):
            data[i] = float(fin.readline())
        conf = session.getDevice('lower_theta')
        conf.setData([length], data)


@usercommand
def LoadCoordinates():
    """
    This function loads the coordinate data from the
    set2D_coords.dat into the f2d_coords device. This
    should only be necessary when this data changes or
    on a new installation. After that, the data should
    reside in the cache.
    """
    xval = []
    yval = []
    dist = []
    eq = []
    az = []
    tth = []
    try:
        coord = session.getDevice('f2d_coords')
    except ConfigurationError:
        session.log.error('2D detector not loaded, cannot load coordinates')
        return
    with open('nicos_sinq/focus/set2D_coords.dat', 'r') as fin:
        line = fin.readline()
        data = line.split()
        coord.xdim = int(data[0])
        coord.ydim = int(data[1])
        line = fin.readline()
        while line:
            data = line.split()
            xval.append(float(data[2]))
            yval.append(float(data[3]))
            dist.append(float(data[4]))
            eq.append(float(data[5]))
            az.append(float(data[6]))
            tth.append(float(data[7]))
            line = fin.readline()
    coord.xval = xval
    coord.yval = yval
    coord.distval = dist
    coord.eqval = eq
    coord.azval = az
    coord.tthval = tth
    session.log.info('2D detector coordinates successfully loaded')


@usercommand
@parallel_safe
def chosta():
    """
    Reports chopper status.
    """
    # Get the configurator device
    FCs = session.getDevice('ch1_speed')
    DCs = session.getDevice('ch2_speed')
    phase = session.getDevice('ch_phase')
    ratio = session.getDevice('ch_ratio')

    session.log.info('FC speed: %d, DC speed %d, phase = %.2f, ratio = %d',
                     FCs.read(), DCs.read(), phase.read(), ratio.read())
    if FCs.target-FCs.read() > FCs.window:
        session.log.info('FC speed target: %d', FCs.target)


@usercommand
@parallel_safe
def setpar():
    """
    Reports instrument setup.
    """
    return chosta()
