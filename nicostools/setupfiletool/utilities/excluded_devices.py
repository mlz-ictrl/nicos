#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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
#   Andreas Schulz <andreas.schulz@frm2.tum.de>
#
# *****************************************************************************

excluded_device_classes = [
    'nicos.core.device.Device',
    'nicos.core.device.Readable',
    'nicos.core.device.Moveable',
    'nicos.core.device.Measurable',
    'nicos.core.device.SubScanMeasurable',
    'nicos.devices.abstract.Coder',
    'nicos.devices.abstract.Motor',
    'nicos.devices.abstract.Axis',
    'nicos.devices.abstract.TransformedReadable',
    'nicos.devices.abstract.TransformedMoveable',
    'nicos.devices.abstract.MappedReadable',
    'nicos.devices.abstract.MappedMoveable',
    'nicos.devices.generic.detector.PassiveChannel',
    'nicos.devices.generic.detector.PostprocessPassiveChannel',
    'nicos.devices.generic.detector.ScanningDetector',
    'nicos.devices.generic.magnet.BipolarSwitchingMagnet',
    'nicos.devices.generic.sequence.BaseSequencer',
    'nicos.devices.generic.sequence.MeasureSequencer',
    'nicos.devices.tas.spectro.TASConstant',
    'nicos.devices.sxtal.instrument.SXTalBase',
]
