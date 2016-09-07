#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

"""Session class used with the NICOS daemon."""

import sys
import threading

from nicos.core import AccessError, ACCESS_LEVELS, User, watchdog_user
from nicos.utils.loggers import INFO
from nicos.core.sessions.utils import LoggingStdout
from nicos.core.sessions.simple import NoninteractiveSession
from nicos.devices.cacheclient import DaemonCacheClient
from nicos.protocols.daemon import BREAK_AFTER_STEP
from nicos.services.daemon.htmlhelp import HelpGenerator
from nicos.pycompat import builtins, exec_, string_types


class DaemonSession(NoninteractiveSession):
    """Subclass of Session that configures the logging system for running under
    the execution daemon: it adds the special daemon handler and installs a
    standard output stream that logs stray output.
    """

    autocreate_devices = True
    cache_class = DaemonCacheClient
    has_datamanager = True

    # later overwritten to send events to the client
    emitfunc = lambda self, event, args: None

    # later overwritten to the real thread ID of the script thread
    script_thread_id = None

    # to set a point where the "break" command can break, it suffices to execute
    # some piece of code in a frame with the filename starting with "<break>";
    # these objects are such a piece of code (the number designates the level)
    _bpcode = [None, compile("pass", "<break>1", "exec"),
               compile("pass", "<break>2", "exec"),
               compile("pass", "<break>3", "exec"),
               compile("pass", "<break>4", "exec"),
               compile("pass", "<break>5", "exec")]

    def _initLogging(self, prefix=None, console=True):
        NoninteractiveSession._initLogging(self, prefix, console)
        sys.displayhook = self._displayhook

    def _displayhook(self, value):
        if value is not None and getattr(value, '__display__', True):
            self.log.log(INFO, repr(value))

    def _beforeStart(self, daemondev):
        from nicos.services.daemon.utils import DaemonLogHandler
        self.daemon_device = daemondev
        self.daemon_handler = DaemonLogHandler(daemondev)
        # create a new root logger that gets the daemon handler
        self.createRootLogger()
        self.log.addHandler(self.daemon_handler)
        sys.stdout = LoggingStdout(sys.stdout)

        # add an object to be used by DaemonSink objects
        self.emitfunc = daemondev.emit_event
        self.emitfunc_private = daemondev.emit_event_private

        # call stop() upon emergency stop
        from nicos.commands.device import stop
        daemondev._controller.add_estop_function(stop, ())

        # pretend that the daemon setup doesn't exist, so that another
        # setup can be loaded by the user
        self.devices.clear()
        self.explicit_devices.clear()
        self.configured_devices.clear()
        self.user_modules.clear()
        self.loaded_setups.clear()
        del self.explicit_setups[:]

        # we have to clear the namespace since the Daemon object and related
        # startup objects are still in there
        self.namespace.clear()
        # but afterwards we have to automatically import objects again
        self.namespace['__builtins__'] = builtins.__dict__
        self.initNamespace()

        self._exported_names.clear()
        self._helper = HelpGenerator()

    def setMode(self, mode):
        NoninteractiveSession.setMode(self, mode)
        self.emitfunc('mode', mode)

    def updateLiveData(self, tag, dtype, nx, ny, nt, time, data):
        self.emitfunc('liveparams', (tag, '', dtype, nx, ny, nt, time))
        self.emitfunc('livedata', data)

    def notifyDataFile(self, tag, filename):
        self.emitfunc('liveparams', (tag, filename, '', 0, 0, 0, 0))
        self.emitfunc('livedata', '')

    def breakpoint(self, level):
        exec_(self._bpcode[level])

    def checkAccess(self, required):
        if 'level' in required:
            script = self.daemon_device.current_script()
            rlevel = required['level']
            if isinstance(rlevel, string_types):
                for k, v in ACCESS_LEVELS.items():
                    if v == rlevel:
                        rlevel = k
                        break
                else:
                    raise AccessError('invalid access level name: %r' % rlevel)
            if script and rlevel > script.userlevel:
                raise AccessError('%s access is not sufficient, %s access '
                                  'is required' % (
                                      ACCESS_LEVELS.get(script.userlevel,
                                                        str(script.userlevel)),
                                      ACCESS_LEVELS.get(rlevel, str(rlevel))))
        return NoninteractiveSession.checkAccess(self, required)

    def checkParallel(self):
        return self.script_thread_id != threading.current_thread().ident

    def showHelp(self, obj=None):
        try:
            data = self._helper.generate(obj)
        except ValueError:
            self.log.info('Sorry, no help exists for %r.' % obj)
            return
        except Exception:
            self.log.warning('Could not generate the help for %r' % obj, exc=1)
            return
        if not isinstance(obj, string_types):
            self.log.info('Showing help in the calling client...')
        self.emitfunc_private('showhelp', data)

    def getExecutingUser(self):
        s = self.daemon_device.current_script()
        return User(s.user, s.userlevel)

    def clientExec(self, func, args):
        """Execute a function client-side."""
        self.emitfunc_private(
            'clientexec', ('%s.%s' % (func.__module__, func.__name__),) + args)

    def setupCallback(self, setupnames, explicit):
        self.emitfunc('setup', (setupnames, explicit))

    def deviceCallback(self, action, devnames):
        self.emitfunc('device', (action, devnames))

    def experimentCallback(self, proposal, proptype):
        """Callback when the experiment has been changed."""
        NoninteractiveSession.experimentCallback(self, proposal, proptype)
        # reset cached messages when switching TO user experiment
        if proptype == 'user':
            del self.daemon_device._messages[:]
        self.emitfunc('experiment', (proposal, proptype))

    def pnpEvent(self, event, *data):
        self.emitfunc('plugplay', (event,) + data)

    def _watchdogHandler(self, key, value, time, expired=False):
        """Handle a watchdog event."""
        if key.endswith('/scriptaction'):
            action, msg = value[1]
            controller = self.daemon_device._controller
            if action == 'stop':
                controller.script_stop(BREAK_AFTER_STEP, watchdog_user, msg)
            elif action == 'immediatestop':
                controller.script_immediate_stop(watchdog_user, msg)
        # handle other cases
        NoninteractiveSession._watchdogHandler(self, key, value, time, expired)

    def watchdogEvent(self, event, time, data):
        """Handle a watchdog alarm event."""
        if event == 'warning':
            self.log.warning('WATCHDOG ALERT: %s' % data)
        self.emitfunc('watchdog', (event, time, data))
