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

"""NICOS daemon package."""

import sys
import time
import traceback
import threading

from nicos import nicos_version, config
from nicos.core import listof, Device, Param, ConfigurationError, host, Attach
from nicos.utils import createThread
from nicos.pycompat import listitems
from nicos.services.daemon.auth import Authenticator
from nicos.services.daemon.script import ExecutionController

from nicos.protocols.daemon.classic import DEFAULT_PORT, Serializer
from nicos.services.daemon.proto.classic import Server


class NicosDaemon(Device):
    """
    This class abstracts the main daemon process.
    """

    attached_devices = {
        'authenticators': Attach('The authenticator devices to use for '
                                 'validating users and passwords',
                                 Authenticator, multiple=True),
    }

    parameters = {
        'server':         Param('Address to bind to (host or host[:port])',
                                type=host, mandatory=True,
                                ext_desc='The default port is ``1301``.'),
        'maxlogins':      Param('Maximum number of simultaneous clients '
                                'served', type=int,
                                default=10),
        'reuseaddress':   Param('Whether to set SO_REUSEADDR', type=bool,
                                default=True),
        'updateinterval': Param('Interval for watch expressions checking and'
                                ' sending updates to the clients',
                                type=float, unit='s', default=0.2),
        'trustedhosts':   Param('A list of trusted hosts allowed to log in',
                                type=listof(str),
                                ext_desc='An empty list means all hosts are '
                                'allowed.'),
        'simmode':        Param('Whether to always start in dry run mode',
                                type=bool),
        'autosimulate':   Param('Whether to simulate scripts when running them',
                                type=bool, default=False)
    }

    def doInit(self, mode):
        self._stoprequest = False
        # the controller represents the internal script execution machinery
        if self.autosimulate and not config.sandbox_simulation:
            raise ConfigurationError('autosimulation configured but sandbox'
                                     ' deactivated')

        self._controller = ExecutionController(self.log, self.emit_event,
                                               'startup', self.simmode,
                                               self.autosimulate)

        # check that all configured authenticators use the same hashing method
        self._pw_hashing = 'sha1'
        auths = self._attached_authenticators
        if auths:
            self._pw_hashing = auths[0].pw_hashing()
            for auth in auths[1:]:
                if self._pw_hashing != auth.pw_hashing():
                    raise ConfigurationError(
                        self, 'incompatible hash methods for authenticators: '
                        '%s requires %r, while %s requires %r' %
                        (auths[0], self._pw_hashing, auth, auth.pw_hashing()))

        # cache log messages emitted so far
        self._messages = []

        address = self.server
        if ':' not in address:
            host = address
            port = DEFAULT_PORT
        else:
            host, port = address.split(':')
            port = int(port)

        self._server = Server(self, (host, port), Serializer())

        self._watch_worker = createThread('daemon watch monitor', self._watch_entry)

    def _watch_entry(self):
        """
        This thread checks for watch value changes periodically and sends out
        events on changes.
        """
        # pre-fetch attributes for speed
        ctlr, intv, emit, sleep = self._controller, self.updateinterval, \
            self.emit_event, time.sleep
        lastwatch = {}
        while not self._stoprequest:
            sleep(intv)
            # new watch values?
            watch = ctlr.eval_watch_expressions()
            if watch != lastwatch:
                emit('watch', watch)
                lastwatch = watch

    def emit_event(self, event, data):
        """Emit an event to all handlers."""
        self._server.emit(event, data)

    def emit_event_private(self, event, data):
        """Emit an event to only the calling handler."""
        handler = self._controller.get_current_handler()
        if handler:
            self._server.emit(event, data, handler)

    def statusinfo(self):
        self.log.info('got SIGUSR2 - current stacktraces for each thread:')
        active = threading._active
        for tid, frame in listitems(sys._current_frames()):
            if tid in active:
                name = active[tid].getName()
            else:
                name = str(tid)
            self.log.info('%s: %s', name,
                          ''.join(traceback.format_stack(frame)))

    def start(self):
        """Start the daemon's server."""
        self.log.info('NICOS daemon v%s started, starting server on %s',
                      nicos_version, self.server)
        # startup the script thread
        self._controller.start_script_thread()
        self._worker = createThread('daemon server', self._server.start,
                                    args=(self._long_loop_delay,))

    def wait(self):
        while not self._stoprequest:
            time.sleep(self._long_loop_delay)
        self._worker.join()

    def quit(self, signum=None):
        self.log.info('quitting on signal %s...', signum)
        self._stoprequest = True
        self._server.stop()
        self._worker.join()
        self._server.close()

    def current_script(self):
        return self._controller.current_script

    def get_authenticators(self):
        return self._attached_authenticators, self._pw_hashing
