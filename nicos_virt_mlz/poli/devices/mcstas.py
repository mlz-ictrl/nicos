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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""VPOLI specific McStas devices."""

from nicos import session
from nicos.core import Override
from nicos.devices.mcstas import McStasSimulation


class PoliSimulation(McStasSimulation):

    parameter_overrides = {
        'mcstasprog': Override(default='POLI'),
        'neutronspersec': Override(default={'localhost': 1.2e6}),
        'intensityfactor': Override(default=1e11),  # for source intensity = 1
    }

    def _prepare_params(self):
        def param(mcstas, nicos=None, f=lambda x: x):
            dev = session.getDevice(nicos or mcstas)
            val = dev.read(0)
            off = getattr(dev, 'offset', 0)
            return '%s=%s' % (mcstas, f(val + off))
        mm2cm = lambda x: x/10

        bpl = session.getDevice('bpl').read(0)
        bpr = session.getDevice('bpr').read(0)
        bpo = session.getDevice('bpo').read(0)
        bpu = session.getDevice('bpu').read(0)

        return [
            # param('wavelength'),
            'bmh=%.2f' % mm2cm(bpl + bpr),
            'bmv=%.2f' % mm2cm(bpo + bpu),
            param('xtrans', f=mm2cm),
            param('ytrans', f=mm2cm),
            # param('chi1'),
            # param('chi2'),
            param('omega'),
            param('gamma'),
            param('liftingctr'),
        ]
