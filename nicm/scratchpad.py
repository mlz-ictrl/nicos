#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   Scratchpad connection for NICM.
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   $Author$
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

from __future__ import with_statement

import re
import time
import socket
import select
import threading


SCRATCHPAD_PORT = 14869

answer_re = re.compile('(?:([0-9.]+)@)?([^:=]+)[:=](.*?)$', re.MULTILINE)


class ScratchPadError(RuntimeError):
    pass


class ScratchPadConnection(object):
    def __init__(self, prefix, host, port=SCRATCHPAD_PORT):
        self.prefix = prefix
        self.address = (host, port)
        self.socket = None
        self.lock = threading.Lock()

    def _connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect(self.address)
        except Exception, err:
            raise ScratchPadError('unable to connect to ScratchPad: %s' % err)

    def _disconnect(self):
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
        except Exception:
            pass

    def _convert(self, value):
        try:
            return float(value)
        except ValueError:
            return value

    def tell(self, key, value, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        msg = '%s@%s=%s\n' % (timestamp, self.prefix + key, value)
        with self.lock:
            if not self.socket:
                self._connect()
            self.socket.send(msg)

    def ask(self, key):
        msg = '%s=\n' % (self.prefix + key)
        with self.lock:
            if not self.socket:
                self._connect()
            self.socket.send(msg)
            sel = select.select([self.socket], [], [self.socket], 3)
            if self.socket in sel[0]:
                answer = self.socket.recv(8192)
                if not answer:
                    raise ScratchPadError('connection to ScratchPad lost')
            elif self.socket in self[2]:
                self._disconnect()
                raise ScratchPadError('connection to ScratchPad lost')
            else:
                raise ScratchPadError('no answer from ScratchPad')
        match = answer_re.match(answer)
        if not match:
            raise ScratchPadError('garbled answer from ScratchPad')
        return self._convert(match.group(2))

    def history(self, key):
        pass


if __name__ == '__main__':
    import sys
    sp = ScratchPadConnection(sys.argv[2], sys.argv[1])
    sp.tell('value', 1)
    while True:
        time.sleep(1)
        print 'asking for value...'
        print sp.ask('value')
