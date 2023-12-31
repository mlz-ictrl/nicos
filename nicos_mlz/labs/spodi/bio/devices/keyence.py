# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
#   Dominik Petz <dominik.petz@frm2.tum.de>
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

import ftplib
import io
import socket
import urllib.request

import numpy as np
from PIL import Image

from nicos import session
from nicos.core.constants import FINAL, MASTER
from nicos.core.params import ArrayDesc, Param, Value, absolute_path, host, \
    intrange, tupleof
from nicos.devices.generic import ActiveChannel, ImageChannelMixin
from nicos.utils import parseHostPort


class KeyenceImage(ImageChannelMixin, ActiveChannel):

    parameters = {
        'trigger_host': Param('Host to trigger a picture',
                              type=host(defaultport=8600),
                              default='keyence.spodi.frm2.tum.de', ),
        'image_server': Param('FTP server to fetch the image',
                              type=host(defaultport=ftplib.FTP_PORT),
                              default='spodiir.spodi.frm2.tum.de', ),
        'image_path': Param('Path on FTP server to fetch the image',
                            type=absolute_path,
                            default='/data/tm-x/image/SD1_001/HEAD-A/', ),
        'image_name': Param('Name of the image file to fetch',
                            type=str, default='0_bild_HEAD-A_NG.bmp', ),
        'size': Param('Detector size in pixels (x, y)',
                      type=tupleof(intrange(1, 2048),
                                   intrange(1, 2048)),
                      settable=False, default=(2048, 2048)),
    }

    def doInit(self, mode):
        # PassiveChannel.doInit(self, mode)
        self.arraydesc = ArrayDesc(self.name, self.size, np.uint8)
        if mode != MASTER:
            return
        try:
            self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.log.debug('Socket Created')
            self.log.debug('%s', self.trigger_host)
            self._client.connect(parseHostPort(self.trigger_host, 8600))
            self.log.debug('Socket Connected to: %s', self.trigger_host)
        except socket.error:
            self._client = None
            self.log.error('Failed to create socket')
            raise

    def valueInfo(self):
        return Value(self.name, unit='a.u.', type='other', fmtstr=self.fmtstr),

    def doStart(self):
        self._trigger()
        session.delay(2)

    def _trigger(self):
        #  Send cmd to send the trigger
        cmd = 'T1\r'  # trigger
        try:
            self._client.send(bytes(cmd, 'ascii'))
            msg = self._client.recv(1024).decode('ascii')
            self.log.debug('%s', msg)
            if msg != cmd:
                self.log.warning(
                    'Wrong reply from Keyence was received: %s', msg)
        except socket.error:
            self.log.error('Failed to send data!')

    def doReadArray(self, quality):
        if quality != FINAL:
            return
        with urllib.request.urlopen(
           f'ftp://{self.image_server}/{self.image_path}/{self.image_name}'
           ) as r:
            arr = np.asarray(Image.open(io.BytesIO(r.read())))
        self.readresult = [arr.sum()]
        host, _port = parseHostPort(self.image_server, ftplib.FTP_PORT)
        with ftplib.FTP(host, 'anonymous') as ftp:
            ftp.delete(f'{self.image_path}/{self.image_name}')
            ftp.close()
        return arr
