#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2015-2017 by the NICOS contributors (see AUTHORS)
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
LAUE specific commands
"""
import numpy as np

from nicos.devices.sxtal.goniometer.posutils import Xrot, Yrot, Zrot
from nicos.devices.sxtal.goniometer.base import PositionFactory
from nicos.commands import usercommand
from nicos.commands.device import maw, move

from nicos import session


@usercommand
def calcEsmeraldaRots(xrot, yrot, zrot):
    """Move goniometer to new position as specified by orienting angles

    *x*,*y*,*z* Orienting angles as determined e.g. by Esmeralda
    """

    try:
        laue = session.getDevice('kappagon')
        cpos = laue.read().With(phi=0)
    except Exception:   # enables standalone testing
        cpos = PositionFactory('k', phi=0, kappa=0, omega=0, theta=0)
    ma = cpos.asG().matrix
    # note: internal coordinate system is different from Esmeralda:
    #  X_E = Y_int
    #  Y_E = -X_int
    #  Z_E = Z_int
    rx = Xrot(np.radians(yrot))
    ry = Yrot(np.radians(-xrot))
    rz = Zrot(np.radians(zrot))
    rotmat = np.dot(rz,np.dot(ry,rx))
    newmat = np.dot(ma, rotmat)
    npos = cpos.asG().With(matrix=newmat)
    return npos.asK()

@usercommand
def rmove(dev, delta):
    move(dev, dev() + delta)

@usercommand
def rmaw(dev, delta):
    maw(dev, dev() + delta)
