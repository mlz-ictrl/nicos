#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

"""Utilies for ZeroMQ messaging."""

import logging
from threading import Thread

import zmq

from nicos import session
from nicos.protocols.daemon import serialize, unserialize
from nicos.utils.loggers import TRANSMIT_ENTRIES


zmq_ctx = zmq.Context()


class SimLogReceiver(Thread):
    """
    Thread for receiving messages from a pipe and sending them to the client.
    """

    def __init__(self, daemon):
        self.socket = zmq_ctx.socket(zmq.PULL)
        self.port = self.socket.bind_to_random_port('tcp://127.0.0.1')
        if daemon is None:
            target = self._console_thread
        else:
            target = self._daemon_thread
        Thread.__init__(self, target=target, args=(self.socket, daemon),
                        name='SimLogReceiver')

    def _daemon_thread(self, socket, daemon):
        while True:
            data = socket.recv()
            msg = unserialize(data)
            if isinstance(msg, list):
                # do not cache these messages
                #daemon._messages.append(msg)
                daemon.emit_event('message', msg)
            else:
                daemon.emit_event('simresult', msg)
                socket.close()
                return

    def _console_thread(self, socket, daemon):
        while True:
            data = socket.recv()
            msg = unserialize(data)
            if isinstance(msg, list):
                record = logging.LogRecord(msg[0], msg[2], msg[5],
                                           0, msg[3], (), None)
                record.message = msg[3].rstrip()
                session.log.handle(record)
            else:
                # In the console session, the summary is printed by the
                # sim() command.
                socket.close()
                return


class SimLogSender(logging.Handler):
    """
    Log handler sending messages to the original daemon via a pipe.
    """

    def __init__(self, port, session):
        logging.Handler.__init__(self)
        self.socket = zmq_ctx.socket(zmq.PUSH)
        self.socket.connect('tcp://127.0.0.1:%d' % port)
        self.session = session
        self.devices = []

    def begin_setup(self):
        self.level = logging.ERROR  # log only errors before code starts

    def begin_exec(self):
        from nicos.core import Readable
        # Collect information on timing and range of all devices
        self.starttime = self.session.clock.time
        for devname, dev in self.session.devices.iteritems():
            if isinstance(dev, Readable):
                self.devices.append(devname)
                dev._sim_min = None
                dev._sim_max = None
        self.level = 0

    def emit(self, record, entries=TRANSMIT_ENTRIES):  #pylint: disable=W0221
        msg = [getattr(record, e) for e in entries]
        if not hasattr(record, 'nonl'):
            msg[3] += '\n'
        self.socket.send(serialize(msg))

    def finish(self):
        stoptime = self.session.clock.time
        devinfo = {}
        for devname in self.devices:
            dev = self.session.devices.get(devname)
            if dev and dev._sim_min is not None:
                try:
                    devinfo[dev] = (dev.format(dev._sim_value),
                                    dev.format(dev._sim_min),
                                    dev.format(dev._sim_max))
                except Exception:
                    pass
        self.socket.send(serialize((stoptime, devinfo)))
