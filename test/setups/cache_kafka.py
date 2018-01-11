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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

import os
from test.utils import alt_cache_addr

name = 'setup for cache stresstest with kafka db'

devices = dict(
    Server = device('nicos.services.cache.server.CacheServer',
        server = alt_cache_addr,
        db = 'DB4',
        loglevel = 'debug',
    ),
    DB4 = device('nicos.services.cache.database.kafka.KafkaCacheDatabaseWithHistory',
        currenttopic = 'test-flatbuffers',
        historytopic = 'test-flatbuffers-history',
        brokers = [os.environ.get('KAFKA_URI', 'localhost:9092')],
        loglevel = 'debug',
        serializer = 'serializer'
    ),
    serializer = device('nicos.services.cache.database.entry.FlatbuffersCacheEntrySerializer'),
)
