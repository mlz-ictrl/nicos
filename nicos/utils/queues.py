#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2018-2020 by the NICOS contributors (see AUTHORS)
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
#   Bjoern Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

"""
In-memory queue implementations for  NICOS
"""

from __future__ import absolute_import, division, print_function

from nicos.pycompat import queue


class SizedQueue(queue.Queue):
    """A Queue that limits the total size of event messages"""
    def _init(self, maxsize):
        assert maxsize > 0
        self.nbytes = 0
        queue.Queue._init(self, maxsize)

    def _qsize(self):
        # limit to self.maxsize because of equality test
        # for full queues in python 2.7
        return min(self.maxsize, self.nbytes)

    def _put(self, item):
        # size of the queue item should never be zero, so add one
        self.nbytes += len(item[1]) + 1
        self.queue.append(item)

    def _get(self):
        item = self.queue.popleft()
        self.nbytes -= len(item[1]) + 1
        return item
