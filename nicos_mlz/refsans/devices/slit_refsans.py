# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#   Matthias Pomm <matthias.pomm@hereon.de>
#
# *****************************************************************************

"""REFSANS specific slit devices."""

from nicos import session

from nicos.devices.generic.slit import Gap as BaseGap, \
    TwoAxisSlit as BaseTwoAxisSlit, VerticalGap as BaseVerticalGap


class Gap(BaseGap):
    """REFSANS special implementation of gap devices consisting of two blades."""

    def _doStartGap(self, target, alb, art):
        f = self.coordinates == 'opposite' and -1 or +1
        tlb, trt = target
        # determine which axis to move first, so that the blades can
        # not touch when one moves first
        clb, crt = alb.read(0), art.read(0)
        clb *= f
        if trt < crt and tlb < clb:
            # both move to smaller values, need to start left/bottom blade
            # first
            alb.maw(tlb * f)
            session.delay(self._delay)
            art.move(trt)
        elif trt > crt and tlb > clb:
            # both move to larger values, need to start right/top blade first
            art.maw(trt)
            session.delay(self._delay)
            alb.move(tlb * f)
        else:
            # don't care
            art.maw(trt)
            alb.move(tlb * f)


class TwoAxisSlit(BaseTwoAxisSlit):
    """REFSANS special implementation ofrectangular slit with 2 orthogonal slits.
    """

    def doStart(self, target):
        th, tv = target
        self._attached_horizontal.maw(th)
        self._attached_vertical.move(tv)


class VerticalGap(BaseVerticalGap, Gap):
    """Refsans special implementattion of a vertical gap."""
