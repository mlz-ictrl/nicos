# - * - encoding: utf-8 - * -
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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************
'''Detector driver for the laue PSL detector via the windows server

  To ease offline testing (without nicos) this is a standalone module without
  NICOS dependencies.
'''

import socket
import zlib


class PSLdrv(object):
    def __init__(self, address='lauedet.laue.frm2', port=50000):
        self.address = address
        self.port = port

    def communicate(self, cmd):
        s = socket.create_connection((self.address, self.port), timeout=30.)
        s.send(cmd + '\n')
        if cmd == "GetImage":
            # Get Image data in chunks
            # the detector first sends a line with size info
            nx, ny, data_len = s.recv(1024).split(';')
            nx, ny, data_len = int(nx), int(ny), int(data_len)
            data = b''
            while 1:
                data += s.recv(data_len)
                if len(data) >= data_len:
                    break

            # default:  data is zlib compressed
            data = ((nx, ny), zlib.decompress(data))
        elif cmd == "Snap":
            # don't wait for a reply, it would block until the end
            # of the exposure before returning 'TRUE'
            data = b''
        else:
            data = s.recv(1024)
        return data


def testcom(cmd):
    psl = PSLdrv()
    return psl.communicate(cmd)
