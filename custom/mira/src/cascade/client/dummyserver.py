#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

import socket, struct, time
import numpy

x = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
x.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
x.bind(('', 1234))
x.listen(1)
ts = 0

#ram = numpy.ones(128 * 128 * 128, '<u4')
ram = numpy.random.randint(0, 10000, 128 * 128 * 128).astype('<u4')

#ram = 'IMAG' + ''.join((chr(i) + '\x00\x00\x00') * 128 for i in range(128))
while True:
    try:
        conn, addr = x.accept()
        print 'got connection'
        while True:
            length = conn.recv(4)
            l, = struct.unpack('i', length)
            cmd = conn.recv(l)
            print 'got cmd:', cmd
            if cmd.startswith('CMD_config_cdr'):
                cfg = dict(v.split('=') for v in cmd[14:-1].split())
                if 'time' in cfg: mt = float(cfg['time'])
                resp = 'OKAY'
            elif cmd.startswith('CMD_start'):
                ts = time.time()
                resp = 'OKAY'
            elif cmd.startswith('CMD_status'):
                resp = 'ERR_stop=%d' % bool(time.time() > ts+mt)
            elif cmd.startswith('CMD_readsram'):
                resp = 'DATA' + ram.tostring()
#                print len(resp)
            elif cmd.startswith('CMD_getconfig_cdr'):
                resp = 'MSG_mode=tof time=1000'
            else:
                resp = 'ERR_unknown command'
            length = struct.pack('i', len(resp))
            conn.send(length + resp)
    except Exception, e:
        print 'EXCEPTION:', e
