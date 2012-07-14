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

"""Session class used with the NICOS daemon."""

__version__ = "$Revision$"

import os
import sys
import signal

from nicos.core import AccessError, ACCESS_LEVELS
from nicos.sessions import Session
from nicos.cache.client import DaemonCacheClient
from nicos.utils.loggers import OUTPUT
from nicos.sessions.utils import LoggingStdout
from nicos.sessions.simple import NoninteractiveSession
from nicos.daemon.htmlhelp import HelpGenerator


class DaemonSession(NoninteractiveSession):
    """
    Subclass of Session that configures the logging system for running under the
    execution daemon: it adds the special daemon handler and installs a standard
    output stream that logs stray output.
    """

    autocreate_devices = True
    cache_class = DaemonCacheClient

    # to set a point where the "break" command can break, it suffices to execute
    # some piece of code in a frame with the filename "<break>"; this object is
    # such a piece of code
    _bpcode = compile("pass", "<break>", "exec")

    def _initLogging(self):
        NoninteractiveSession._initLogging(self)
        sys.displayhook = self._displayhook

    def _displayhook(self, value):
        if value is not None:
            self.log.log(OUTPUT, repr(value))

    def _beforeStart(self, daemondev):
        from nicos.daemon.utils import DaemonLogHandler
        self.daemon_device = daemondev
        self.daemon_handler = DaemonLogHandler(daemondev)
        # create a new root logger that gets the daemon handler
        self.createRootLogger()
        self.log.addHandler(self.daemon_handler)
        sys.stdout = LoggingStdout(sys.stdout)

        # add an object to be used by DaemonSink objects
        self.emitfunc = daemondev.emit_event

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

        # load all default modules from now on
        self.auto_modules = Session.auto_modules

        self._exported_names.clear()
        self._helper = HelpGenerator()

    def forkSimulation(self, code, wait=True):
        from nicos.daemon.utils import SimLogSender, SimLogReceiver
        rp, wp = os.pipe()
        receiver = SimLogReceiver(rp, self.daemon_device)
        receiver.start()
        try:
            pid = os.fork()
        except OSError:
            self.log.exception('Cannot fork into simulation mode')
            return
        if pid == 0:
            # child process
            signal.alarm(600)   # kill forcibly after 10 minutes
            pipesender = SimLogSender(wp, self)
            pipesender.begin()
            try:
                self.log.manager.globalprefix = '(sim) '
                self.addLogHandler(pipesender)
                self.setMode('simulation')
                exec code in self.namespace
            except:  # really *all* exceptions
                self.log.exception()
            finally:
                pipesender.finish()
                sys.exit()
            os._exit()
        # parent process
        if wait:
            try:
                os.waitpid(pid, 0)
            except OSError:
                self.log.exception('Error waiting for simulation process')

    def updateLiveData(self, tag, filename, dtype, nx, ny, nt, time, data):
        self.emitfunc('liveparams', (tag, filename, dtype, nx, ny, nt, time))
        self.emitfunc('livedata', data)

    def breakpoint(self, level):
        exec self._bpcode

    def clearExperiment(self):
        # reset cached messages
        del self.daemon_device._messages[:]

    def checkAccess(self, required):
        if 'level' in required:
            script = self.daemon_device.current_script()
            rlevel = required['level']
            if script and rlevel <= script.userlevel:
                raise AccessError('user level not sufficient: %s access is '
                    'required' % ACCESS_LEVELS.get(rlevel, str(rlevel)))
        return NoninteractiveSession.checkAccess(self, required)

    def showHelp(self, obj=None):
        try:
            data = self._helper.generate(obj)
        except ValueError:
            self.log.info('Sorry, no help exists for %r.' % obj)
            return
        except Exception:
            self.log.warning('Could not generate the help for %r' % obj, exc=1)
            return
        if not isinstance(obj, str):
            self.log.info('Showing help in the client\'s help window...')
        self.emitfunc('showhelp', data)
