#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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


class CacheEntry(object):
    __slots__ = ('time', 'ttl', 'value', 'expired')

    def __init__(self, time, ttl, value):
        self.time = time
        self.ttl = ttl
        self.value = value
        self.expired = False

    def __repr__(self):
        if self.expired:
            return '(%s+%s@%s)' % (self.time, self.ttl, self.value)
        return '%s+%s@%s' % (self.time, self.ttl, self.value)
