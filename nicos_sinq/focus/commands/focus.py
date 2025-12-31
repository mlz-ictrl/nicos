# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
from nicos.utils import findResource

__all__ = [
    'ShowTimeBinning', 'UpdateTimeBinning', 'LoadThetaArrays', 'chosta',
    'instpar', 'sampar',
]


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

    # Delay that that each MDIF should be set to
    dt = start / 10.

    tof = session.getDevice('hm_tof_array')
    # For configuration we start at 0
    tof.updateTimeBins(0, step, count)

    # Now configure all, possibly four HM
    for hm in hms:
        try:
            cfg = session.getDevice(hm + '_configurator')
            cfg.updateConfig()

            # only try to set the mdif if the configurator is available
            mdif = session.getDevice('mdif_' + hm)
            mdif.maw(dt)
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
    with open(findResource('nicos_sinq/focus/focusmerge.dat'),
              encoding='utf-8') as fin:
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
    with open('nicos_sinq/focus/set2D_coords.dat', 'r', encoding='utf-8') \
            as fin:
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
    if not FCs.isAtTarget():
        session.log.info('FC speed target: %d', FCs.target)


@usercommand
@parallel_safe
def instpar():
    """
    Reports instrument setup.
    """
    devs = ['mex', 'mtt', 'mth']
    mex = session.getDevice('mex')
    if mex.read(0) < 90:
        devs += ['m1cv', 'm1ch']
    else:
        devs += ['m2cv', 'm2ch']

    devs += ['wavelength', 'em_td', 'em_aw']
    msg = '\n'
    for d in devs:
        msg += '%s = %f\n' % (d, session.getDevice(d).read(0))
    FCs = session.getDevice('ch1_speed')
    DCs = session.getDevice('ch2_speed')
    phase = session.getDevice('ch_phase')
    msg += 'fermispeed = %d set = %d\n' % (FCs.read(0), FCs.target)
    msg += 'diskpeed = %d set = %d\n' % (DCs.read(0), DCs.target)
    msg += 'phase = %f set = %f\n' % (phase.read(0), phase.target)
    tof = session.getDevice('hm_tof_array')
    msg += 'hm delay: %d musec, ch width: %d musec, number of channels: %d\n'\
           % (tof.data[0], tof.data[1] - tof.data[0], len(tof.data))
    session.log.info(msg)


setpar = instpar


@usercommand
@parallel_safe
def sampar():
    """
    Reports user parameters
    """
    msg = '\n'
    msg += '%s:%s\n' % (session.experiment.users,
                        session.experiment.sample.samplename)
    msg += 'Runnumber: %d\n' % session.experiment.lastscan
    det = session.getDevice('focusdet')
    vals = det.read(0)
    msg += 'Monitor: %d; Set: %d; Time: %f h\n' % \
           (vals[1], vals[6], vals[0]/3600.)
    session.log.info(msg)
