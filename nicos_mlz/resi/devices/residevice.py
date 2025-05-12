# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
Created on 30.05.2011

@author: pedersen
"""

import math
import sys

from nicos import session
from nicos.core import Attach, Moveable, NicosError, Param, vec3
from nicos.core.device import DeviceMetaInfo, DeviceParInfo
from nicos.core.status import BUSY, OK
from nicos.devices.sample import Sample

sys.path.append('/home/resi/pedersen/workspace/singlecounter')
sys.path.append('/home/resi/pedersen/workspace/nonius_new/app')


# imports from the nonius libs
try:
    from goniometer import position
    from sc_scan_new import HuberScan
except ImportError as e:
    # at least make the module importable for setup checking
    session.log.info(e)
    HuberScan = None
    position = None


class ResiPositionProxy:
    """
    proxy class to make  position objects really picklable

    see: http://code.activestate.com/recipes/252151-generalized-delegates-and-proxies/
    """
    __hardware = None
    pos = None

    def __init__(self, pos):
        #super(ResiPositionProxy, self).__init__(pos)
        self.pos = pos

    @classmethod
    def SetHardware(cls, hw):
        ResiPositionProxy.__hardware = hw

    def __getattr__(self, name):
        return getattr(self.pos, name)
    def __setattr__(self, name, value):
        if name == 'pos':
            self.__dict__[name] = value
        elif self.pos:
            return setattr(self.pos, name, value)

    def __repr__(self):
        return self.pos.__repr__()

    def __getstate__(self):
        return self.pos.storable()
    def __setstate__(self, state):
        self.pos = position.PositionFromStorage(ResiPositionProxy.__hardware, state)


class ResiDevice(Moveable):
    """
    Main device for RESI

     * talks to the HUBER controller for all 4 axes.
     * handles cell calculations

    """
    name = None

    def doPreinit(self, mode):
        """
        Constructor
        """
        # the hardware will use a dummy driver if no hardware is detected
        if HuberScan is None:
            raise NicosError(self, 'Nonius scan libraries not found on this '
                             'system, cannot use ResiDevice')
        self._hardware = HuberScan()
        try:
            self._hardware.LoadRmat()
        except RuntimeError as e:
            print(e)
            print('Setting a default cell (quartz): 4.9287,4.9827,5.3788, 90,90,120')
            self._hardware.SetCellParam(a=4.9287, b=4.9287, c=5.3788, alpha=90.000, beta=90.000, gamma=120.000)
        self._hardware.cell.conventionalsystem = 'triclinic'
        self._hardware.cell.standardize = 0
        self._hardware.cell.pointgroup = '1'
        self._hardware.bisect.cell = self._hardware.cell
        ResiPositionProxy.SetHardware(self._hardware)
        #self.loglevel='debug'

    def doRead(self, maxage=0):
        return ResiPositionProxy(self._hardware.GetPosition(maxage))

    def doStart(self, target):
        self._hardware.Goto(**target)

    def doStatus(self, maxage=0):
        statusmap = {0: (OK, 'idle'), 1: (BUSY, 'moving')}
        hwstatus = self._hardware.hw.hwll.isrunning()
        return statusmap[hwstatus][0], statusmap[hwstatus][1]

    def doInfo(self):
        info = []
        pos = ResiPositionProxy(self._hardware.GetPosition())
        info.append(
            DeviceMetaInfo('position',
                           DeviceParInfo(pos, str(pos), '', 'experiment')))
        info.append(
            DeviceMetaInfo('reflex',
                           DeviceParInfo(self._hardware.current_reflex,
                                         str(self._hardware.current_reflex),
                                         '', 'experiment')))
        info.append(
            DeviceMetaInfo('cell',
                           DeviceParInfo(self._hardware.cell,
                                         str(self._hardware.cell), '',
                                         'sample')))
        return info

    def doStop(self):
        self._hardware.hw.Abort()
        self._hardware.Finish()

    def dogetScanDataSet(self, **kw):
        """ Get a list of reflections to scan from the unit cell information

        arguments: either thmin/thmax  or dmin/dmax have to be specified
        """
        return self._hardware.getScanDataset(**kw)


class ResiVAxis(Moveable):
    """ResiVAxis: Virtual single axes for RESI

    this device exports a single axis from the resi device
    """
    attached_devices = {
        'basedevice': Attach('the base device', ResiDevice)
    }
    parameters = {
        'mapped_axis': Param('Mapped axis', type=str, mandatory=True)
    }
    def doStart(self, target):
        self._attached_basedevice.start({self.mapped_axis:target})
    def doRead(self, maxage=0):
        return math.degrees(getattr(self._attached_basedevice.read(maxage), self.mapped_axis))
    def doIsCompleted(self):
        # the moves are currently blocking due to restrictions in the underlying hardware access layer.
        return True


class ResiSample(Sample):
    """Cell object representing sample geometry."""
    attached_devices = {
        'basedevice': Attach('the base device', ResiDevice)
    }
    parameters = {
        'lattice': Param('Lattice constants', type=vec3, settable=True,
                         default=[5, 5 , 5], unit='A',
                         category='sample'),
        'angles':  Param('Lattice angles', type=vec3, settable=True,
                         default=[90, 90, 90], unit='deg', category='sample'),
    }
    def doRead(self, maxage=0):
        return repr(self._attached_basedevice.cell)
