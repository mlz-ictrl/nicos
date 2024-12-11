# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
from nicos import session
from nicos.commands import parallel_safe, usercommand
from nicos.commands.basic import NewSetup

__all__ = [
    'checkzebra', 'zebraconf',
]

@usercommand
@parallel_safe
def checkzebra():
    """
    Check the system status of ZEBRA and report on errors
    """
    ok = True
    devices = ['opt_bench_p', 'beam_exit_p', 'exc_count',
               'shutter_error', 'w1_p', 'w2_p', 'w1_c', 'w2_c']
    for d in devices:
        dev = session.getDevice(d)
        val = dev.read(0)
        if val == 1:
            session.log.error(dev.description)
            ok = False
    if ok:
        session.log.info('ZEBRA is healthy and happily grazing neutrons')
    else:
        session.log.error('ZEBRA has problems, get a licenced '
                          'ZEBRA veterinarian to fix the problem')


@usercommand
def zebraconf():
    """
    This reads the ZEBRA SPS and tries to configure ZEBRA from the data
    found.
    """
    to_add = {}
    to_remove = {}

    # Configuring tables of setups to add or remove for various
    # conditions. Note: the keys have to match device names in the
    # SPS setup
    to_add['w1'] = ['wagen1']
    to_remove['w1'] = ['wagen2']

    to_add['w2'] = ['wagen2', 'detector_single']
    to_remove['w2'] = ['wagen1', 'detector_2d']

    to_add['twod'] = ['detector_2d']
    to_remove['twod'] = ['detector_single']

    to_add['euler_present'] = ['zebraeuler']
    to_remove['euler_present'] = ['zebratas', 'zebranb']

    ana = False
    setups = list(session.loaded_setups)
    # pylint: disable=consider-using-dict-items
    for d in to_add:
        dev = session.getDevice(d)
        if dev.read(0):
            session.log.info('Configuring for %s',  dev.description)
            for s in to_remove[d]:
                if s in setups:
                    setups.remove(s)
            for s in to_add[d]:
                if s not in setups:
                    setups.append(s)
            if d == 'w2':
                ana = True
    NewSetup(*setups)
    if ana:
        wldev = session.getDevice('wavelength')
        wl = wldev.read(0)
        session.log.info('Driving analyzer to %f', wl)
        anadev = session.getDevice('ana')
        anadev.maw(wl)
