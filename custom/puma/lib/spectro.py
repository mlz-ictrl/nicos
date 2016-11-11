#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Custom TAS instrument class for PUMA."""
# derived from the PANDA one ....

# !!! keep in sync with the custom/puma/setups/lengths.py setup file !!!

from nicos import session
from nicos.devices.tas import TAS


class PUMA(TAS):

    def _getCollimation(self):
        ret = []
        for devname in ['ca1', 'ca2', 'ca3', 'ca4']:
            try:
                dev = session.getDevice(devname)
                coll = dev.read()
            except Exception:
                self.log.warning('could not read collimation %s', devname,
                                 exc=1)
                coll = 'none'
            if coll == 'none':
                ret.append(6000)
            elif coll.endswith('m'):
                try:
                    ret.append(float(coll[:-1]))
                except Exception:
                    self.log.warning('unknown collimation setting %r for %s',
                                     coll, devname)
                    ret.append(6000)
            else:
                self.log.warning('unknown collimation setting %r for %s',
                                 coll, devname)
                ret.append(6000)

        for devname in ['cb1', 'cb2', 'cb3', 'cb4']:
            try:
                dev = session.getDevice(devname)
                coll = dev.read()
            except Exception:
                self.log.warning('could not read collimation %s', devname,
                                 exc=1)
                ret.append(6000)
            else:
                ret.append(coll)

        return ret

    def _getResolutionParameters(self):
        # read lengths
        lengths = {}
        for devname in ['lsm', 'lms', 'lsa', 'lad']:
            try:
                dev = session.getDevice(devname)
                l = dev.read()
            except Exception:
                self.log.warning('could not read %s', devname, exc=1)
                l = 100
            lengths[devname] = l

        return [
            1,     # circular (0) or rectangular (1) source
            14.0,  # width of source / diameter (cm)
            9.0,   # height of source / diameter (cm)
            0,     # no guide (0) or guide (1)
            1,     # horizontal guide divergence (min/AA)
            1,     # vertical guide divergence (min/AA)

            1,     # cylindrical (0) or cuboid (1) sample
            1.0,   # sample width / diameter perp. to Q (cm)
            1.0,   # sample width / diameter along Q (cm)
            1.0,   # sample height (cm)

            1,     # circular (0) or rectangular (1) detector
            2.54,  # width / diameter of the detector (cm)
            10.0,  # height / diameter of the detector (cm)

            # may need to depend on the actual monochromator !
            0.2,   # thickness of monochromator (cm)
            26.0,  # width of monochromator (cm)
            16.2,  # height of monochromator (cm)

            0.2,   # thickness of analyzer (cm)
            21.0,  # width of analyzer (cm)
            15.0,  # height of analyzer (cm)

            lengths['lsm'],  # distance source - monochromator (cm)
            lengths['lms'],  # distance monochromator - sample (cm)
            lengths['lsa'],  # distance sample - analyzer (cm)
            lengths['lad'],  # distance analyzer - detector (cm)

            # automatically calculated from focmode and ki if they are zero
            0,     # horizontal curvature of monochromator (1/cm)
            0,     # vertical curvature of monochromator (1/cm)
            0,     # horizontal curvature of analyzer (1/cm)
            0,     # vertical curvature of analyzer (1/cm)

            110,   # distance monochromator - monitor (cm) XXX
            4.0,   # width of monitor (cm)
            10.0,  # height of monitor (cm)
        ]
