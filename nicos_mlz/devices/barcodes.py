#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Device to receive and interpret barcode input at instruments."""

from __future__ import absolute_import, division, print_function

import re
import time
import urllib

from nicos import session
from nicos.core import SIMULATION, Param, dictof
from nicos.core.utils import USER, User
from nicos.devices.tango import StringIO
from nicos.services.daemon.script import RequestError, ScriptRequest
from nicos.utils import createThread


class BarcodeInterpreter(StringIO):
    """Receives input from a connected barcode reader Tango device and executes
    corresponding actions as scripts in the NICOS daemon.

    - Currently recognized barcodes must be in QR-Code format and should
      contain an URI of this format::

         nicos+cmd://Command/arg1/arg2/...

      For example, ::

          nicos+cmd://maw/shutter1/"open"

      to execute `maw(shutter1, "open")`.

    - This device supports assigning shortcuts in the `commandmap` parameter.
      The `Command` in the URI is looked up in the map, and if found, the
      corresponding code is executed, with URI path arguments represented
      by `$0`, `$1` and so forth.

      For example, for this command map ::

         { 'SE': 'NewSetup("$0"); printinfo("Loaded $1 $0")' }

      and this QR-Code content ::

         nicos+cmd://SE/ccr0/cryostat

      NICOS will execute `NewSetup("ccr0"); printinfo("Loaded cryostat ccr0")`.

    Executed commands are run at `USER` level by a special user named like this
    device is called in the setup.
    """

    parameters = {
        'commandmap': Param('Mapping of short commands to Python code',
                            type=dictof(str, str), mandatory=True),
    }

    _thread = None
    _stoprequest = False

    def doInit(self, mode):
        if mode != SIMULATION:
            daemon = getattr(session, 'daemon_device', None)
            if daemon:
                self._thread = createThread('barcode receiver',
                                            self._thread_func, (daemon,))

    def doShutdown(self):
        self._stoprequest = True

    def _thread_func(self, daemon):
        user = User(name=self.name, level=USER)
        controller = daemon._controller
        error_occurred = False
        while not self._stoprequest:
            try:
                barcode = self.readLine()
                if not barcode:
                    # The Tango call will do a blocking poll with typically 2s
                    # timeout, so we don't need another sleep here.
                    continue
                script = self._convert_code(*barcode.split(',', 1))
                if not script:
                    # Let the user know that the code was not recognized.
                    self._dev.Beep(12)
                    continue
                try:
                    controller.new_request(ScriptRequest(
                        script, '<barcode request>', user))
                except RequestError:
                    self.log.warning('could not initiate request from barcode',
                                     exc=1)
                    self._dev.Beep(12)
                else:
                    # Acknowledge receipt and execution.
                    self._dev.Beep(25)
                error_occurred = False
            except Exception:
                # Happens e.g. when the Tango server is restarted during a
                # readLine call.  Log only once, to avoid continuous spamming.
                if not error_occurred:
                    self.log.warning('error waiting for barcode', exc=1)
                    error_occurred = True
                # Also leave some time inbetween attempts; if the Tango server
                # is not coming back we don't want to busy-loop.
                time.sleep(3)

    def _convert_code(self, codetype, content):
        """Convert a barcode of given type and content to Python code to
        execute.
        """
        if codetype == 'QR':
            try:
                res = urllib.parse.urlparse(content)
                if not res.scheme.startswith('nicos+'):
                    return
            except ValueError:
                return
            if res.scheme == 'nicos+cmd':
                cmd = res.netloc
                args = res.path.split('/')
                if cmd in self.commandmap:
                    code = re.sub(r'\$(\d)', lambda m: args[int(m.group(1))],
                                  self.commandmap[cmd])
                else:
                    code = '%s(%s)' % (cmd, ', '.join(args[1:]))
                return code
        elif codetype == 'Code 128' and content.isdigit():
            # shortcut for samples from sample database
            # XXX: proposals use the same barcode type without distinction
            # return 'NewSampleFromDatabase(%s)' % content
            pass
