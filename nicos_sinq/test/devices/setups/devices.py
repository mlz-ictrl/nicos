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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

name = 'Special devices for SINQ'

description = 'Test setup for the SINQ special devices'

devices = dict(
    dev = device('nicos.core.device.Readable', unit = ''),
    dev_preset = device('nicos_sinq.devices.channel.ReadableToChannel',
        precision = 0.1,
        window = 5,
        dev = 'dev'
    ),
    image_forwarder_sink = device('nicos_sinq.test.devices.test_det_image_forwarder.MockImageForwarderSink',
        brokers = ['localhost:9092'],
        output_topic = 'TEST_detector',
    ),
)
