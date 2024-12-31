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
#   Tobias Weber <tobias.weber@frm2.tum.de>
#
# *****************************************************************************

name = 'test slit'

includes = ['stdsystem']

devices = dict(
    m_left = device('test.utils.TestReferenceMotor',
        unit = 'mm',
        abslimits = (-10, 20),
    ),
    m_right = device('test.utils.TestReferenceMotor',
        unit = 'mm',
        abslimits = (-20, 10),
    ),
    m_bottom = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        abslimits = (-20, 10),
    ),
    m_top = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        abslimits = (-10, 20),
    ),
    slit = device('nicos.devices.generic.Slit',
        left = 'm_left',
        right = 'm_right',
        bottom = 'm_bottom',
        top = 'm_top',
    ),
    slit2 = device('nicos.devices.generic.Slit',
        left = 'm_left',
        right = 'm_right',
        bottom = 'm_bottom',
        top = 'm_top',
        coordinates = 'opposite',
    ),
    slit3 = device('nicos.devices.generic.Slit',
        left = 'm_left',
        right = 'm_right',
        bottom = 'm_bottom',
        top = 'm_top',
        opmode = 'centered',
        parallel_ref = True,
    ),
    hgap = device('nicos.devices.generic.slit.HorizontalGap',
        left = 'm_left',
        right = 'm_right',
    ),
    hgap2 = device('nicos.devices.generic.slit.HorizontalGap',
        left = 'm_left',
        right = 'm_right',
        coordinates = 'opposite',
    ),
    hgap3 = device('nicos.devices.generic.slit.HorizontalGap',
        left = 'm_left',
        right = 'm_right',
        opmode = 'centered',
        parallel_ref = True,
    ),
    hgap_overlap = device('nicos.devices.generic.slit.HorizontalGap',
        left = 'm_left',
        right = 'm_right',
        min_opening = -1,
    ),
    hgap_open = device('nicos.devices.generic.slit.HorizontalGap',
        left = 'm_left',
        right = 'm_right',
        min_opening = 1,
    ),
    vgap = device('nicos.devices.generic.slit.VerticalGap',
        bottom = 'm_bottom',
        top = 'm_top',
    ),
    vgap2 = device('nicos.devices.generic.slit.VerticalGap',
        bottom = 'm_bottom',
        top = 'm_top',
        coordinates = 'opposite',
    ),
    vgap3 = device('nicos.devices.generic.slit.VerticalGap',
        bottom = 'm_bottom',
        top = 'm_top',
        opmode = 'centered',
        parallel_ref = True,
    ),
    vgap_overlap = device('nicos.devices.generic.slit.VerticalGap',
        bottom = 'm_bottom',
        top = 'm_top',
        min_opening = -1,
    ),
    vgap_open = device('nicos.devices.generic.slit.VerticalGap',
        bottom = 'm_bottom',
        top = 'm_top',
        min_opening = 1,
    ),
)
