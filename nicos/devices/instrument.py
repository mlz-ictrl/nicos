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

"""NICOS Instrument device."""

from nicos.core import Device, Param, mailaddress


class Instrument(Device):
    """A special singleton device to represent the instrument.

    This class can be subclassed for specific instruments to e.g. provide the
    notion of moving "the instrument" in HKL space, such as in `.TAS`.

    The instrument singleton is available at runtime as
    `nicos.session.instrument`.
    """

    parameters = {
        'facility': Param('Facility name', type=str, category='experiment',
                          settable=False,
                          default='Heinz Maier-Leibnitz Zentrum Garching (MLZ)'),
        'instrument': Param('Instrument name', type=str, category='experiment'),
        'doi': Param('Instrument DOI', type=str, category='experiment',
                     userparam=False),
        'responsible': Param('Instrument responsible name and email',
                             mandatory=True, type=mailaddress,
                             category='experiment'),
        'countloopdelay': Param('Loop delay in checking for counting finished',
                                type=float, default=0.025, userparam=False),
    }
