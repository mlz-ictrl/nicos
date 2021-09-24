#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Kirill Pshenichnyi <pshcyrill@mail.ru>
#
# *****************************************************************************

""" Nexus data template for NERO """

import numpy as np

from nicos.nexus.nexussink import NexusElementBase


class FileName(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        filename = sinkhandler.manager.getFilenames(
            sinkhandler.dataset,
            sinkhandler.sink.filenametemplate,
            sinkhandler.sink.subdir
        )[0]
        dtype = 'S%d' % (len(filename.encode('utf-8')) + 1)
        dset = h5parent.create_dataset(name, (1,), dtype)
        dset[0] = np.array(filename.encode('utf-8'), dtype=dtype)
