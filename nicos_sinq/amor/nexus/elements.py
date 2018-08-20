#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from nicos_ess.nexus.elements import KafkaStream


class HistogramStream(KafkaStream):

    stream_keys = KafkaStream.stream_keys + ['data_type', 'error_type',
                                             'edge_type', 'shape']

    def __init__(self, detector, channel, dataset_names, topic, source,
                 module='hs00'):
        KafkaStream.__init__(self)
        self.detector = detector
        self.channel = channel
        self.dataset_names = dataset_names
        self.set('topic', topic)
        self.set('source', source)
        self.set('writer_module', module)

    def structure(self, name, metainfo):
        desc = metainfo.get((self.detector, 'desc_' + self.channel))

        if not desc:
            return {}

        desc = desc[0]

        self.set('data_type', str(desc['dtype']))
        self.set('error_type', 'float')
        self.set('edge_type', 'float')

        shape = []
        for ax_no in range(len(self.dataset_names)):
            shape.append({
                'dataset_name': self.dataset_names[ax_no],
                'size': desc['shape'][ax_no],
                'label': desc['dimnames'][ax_no],
                'unit': desc['dimunits'][ax_no],
                'edges': desc['dimbins'][ax_no]
            })

        self.set('shape', shape)
        self.store_latest_into(name)
        return KafkaStream.structure(self, name, metainfo)
