# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Alexander Zaft <a.zaft@fz-juelich.de>
#
# *****************************************************************************

"""Device to receive and interpret barcode input at instruments."""

import re
import urllib
from collections import namedtuple

import tango

from nicos import session
from nicos.core import SIMULATION, Param, dictof, intrange
from nicos.core.utils import USER, User
from nicos.devices.entangle import StringIO
from nicos.services.daemon.script import RequestError, ScriptRequest


class BarcodeInterpreterMixin:
    """Mixin for SECoP barcode devices.

    Receives updates from a connected barcodereader Secop device and executes
    corresponding actions as scripts in the NICOS daemon.

    Right now, this Mixin only works for the ZebraBarcodeReader from Frappy.
    Generalizing this would have to make 'decoded' configurable and may need to
    consider the calls to the beep()-command on self.

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

    def doInit(self, mode):
        if hasattr(super(), 'doInit'):
            super().doInit(mode)
        if mode != SIMULATION:
            self._daemon = getattr(session, 'daemon_device', None)
            self.register_callback(
                # move 'decoded' to be a configurable parameter, if needed
                'decoded', lambda mod, param, item: self.on_update(item)
            )

    def on_update(self, item):
        barcode = item.value
        if not barcode:
            return
        user = User(name=self.name, level=USER)
        if not self._daemon:
            return  # probably raise error
        controller = self._daemon._controller
        script = self._convert_code(*barcode.split(',', 1))
        if not script:
            # Let the user know that the code was not recognized.
            self.beep(12)
            return
        try:
            controller.new_request(ScriptRequest(
                script, '<barcode request>', user))
        except RequestError:
            self.log.warning('could not initiate request from barcode',
                             exc=1)
            self.beep(12)
        else:
            # Acknowledge receipt and execution.
            self.beep(25)

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


class TangoAttrCb:
    """An base callback class for Tango events"""

    def __init__(self, device):
        self._device = device
        self._tango_device = device._dev


class TangoAvailableLinesCb(TangoAttrCb):
    """Callback class for Tango events of the AvailableLines attributes."""

    def __init__(self, device, daemon):
        TangoAttrCb.__init__(self, device)
        self._user = User(name=device.name, level=USER)
        self._controller = daemon._controller if daemon else None

    def push_event(self, *args, **kwargs):
        """callback method receiving the event"""
        event_data = args[0]
        if event_data.attr_value and event_data.attr_value.value:
            try:
                barcode = self._tango_device.readLine()
                self._device.on_update(namedtuple('Item', ['value'])(value=barcode))
            except Exception:
                pass


class BarcodeInterpreter(BarcodeInterpreterMixin, StringIO):
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
        'pollinterval': Param('Polling interval for attributes',
                              unit='ms', fmtstr='%d',
                              default=100, settable=False,
                              type=intrange(1, 24 * 3600 * 1000)),
    }

    _availablelines_id = None

    def register_callback(self, mode, cb):
        self._registerAvailableLines()

    def doShutdown(self):
        self._unregisterAvailableLines()

    def _registerAvailableLines(self):
        """Register 'availableLines' events"""
        attr_name = 'availableLines'
        self._dev.poll_attribute(attr_name, self.pollinterval)
        al = self._dev.get_attribute_config(attr_name)
        al.events.ch_event.abs_change = '1'
        self._dev.set_attribute_config(al)
        self._availablelines_id = self._dev.subscribe_event(
            attr_name, tango.EventType.CHANGE_EVENT,
            TangoAvailableLinesCb(self, self._daemon))

    def _unregisterAvailableLines(self):
        """Unregister 'availableLines' events"""
        if self._availablelines_id:
            self._dev.unsubscribe_event(self._availablelines_id)

    def beep(self, pattern):
        self._dev.Beep(pattern)
