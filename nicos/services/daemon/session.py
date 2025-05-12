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
#
# *****************************************************************************

"""Session class used with the NICOS daemon."""

import builtins
import sys
import threading
from uuid import uuid1

from nicos.core import ACCESS_LEVELS, AccessError, watchdog_user
from nicos.core.constants import FILE
from nicos.core.sessions.simple import NoninteractiveSession
from nicos.core.sessions.utils import LoggingStdout
from nicos.devices.cacheclient import DaemonCacheClient
from nicos.protocols.daemon import BREAK_AFTER_STEP, BREAK_NOW
from nicos.services.daemon.htmlhelp import HelpGenerator
from nicos.services.daemon.pyctl import ControlStop
from nicos.utils.loggers import INFO

# This interval, in minutes, is used to notify users of the script being still
# in pause.  The first notification is after this interval, with subsequent
# notifications following every 3 times this interval.
PAUSE_NOTIFICATION_INTERVAL = 10


class DaemonSession(NoninteractiveSession):
    """Subclass of Session that configures the logging system for running under
    the execution daemon: it adds the special daemon handler and installs a
    standard output stream that logs stray output.
    """

    autocreate_devices = True
    cache_class = DaemonCacheClient

    # later overwritten to send events to the client
    emitfunc = lambda self, event, args: None

    # later overwritten to the real thread ID of the script thread
    script_thread_id = None

    # to set a point where the "break" command can break, it suffices to execute
    # some piece of code in a frame with the filename starting with "<break>";
    # these objects are such a piece of code (the number designates the level)
    _bpcode = [None, compile('pass', '<break>1', 'exec'),
               compile('pass', '<break>2', 'exec'),
               compile('pass', '<break>3', 'exec'),
               compile('pass', '<break>4', 'exec'),
               compile('pass', '<break>5', 'exec')]

    _user_prompt = None
    _user_input = Ellipsis

    def _initLogging(self, prefix=None, console=True):
        NoninteractiveSession._initLogging(self, prefix, console)
        sys.displayhook = self._displayhook

    def _displayhook(self, value):
        if value is not None and getattr(value, '__display__', True):
            self.log.log(INFO, repr(value))

    def _beforeStart(self, maindev, daemonized):
        from nicos.services.daemon.utils import DaemonLogHandler
        self.daemon_device = maindev
        self.daemon_handler = DaemonLogHandler(self.daemon_device)
        # create a new root logger that gets the daemon handler
        self.createRootLogger(console=not daemonized)
        self.log.addHandler(self.daemon_handler)

        # We don't want all output to end up on stdout, which is usually either
        # /dev/null or the systemd journal.
        sys.stdout = LoggingStdout()

        # add an object to be used by DaemonSink objects
        self.emitfunc = self.daemon_device.emit_event
        self.emitfunc_private = self.daemon_device.emit_event_private

        # call stop() upon emergency stop
        from nicos.commands.device import stop
        self.daemon_device._controller.add_estop_function(stop, ())

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
        # but afterward we have to automatically import objects again
        self.namespace['__builtins__'] = builtins.__dict__
        self.initNamespace()

        self._exported_names.clear()
        self._helper = HelpGenerator()

    def setMode(self, mode):
        NoninteractiveSession.setMode(self, mode)
        self.emitfunc('mode', mode)

    def updateLiveData(self, parameters, databuffers, labelbuffers=None):
        if labelbuffers is None:
            labelbuffers = []
        self.emitfunc('livedata', parameters, databuffers + labelbuffers)

    def notifyDataFile(self, ftype, uid, detector, filename_or_filenames):
        if isinstance(filename_or_filenames, str):
            filenames = [filename_or_filenames]
        else:
            filenames = filename_or_filenames
        filedescs = [{'filename': fname, 'fileformat': ftype}
                     for fname in filenames]
        params = dict(
            uid=uid,
            time=0,
            det=detector,
            tag=FILE,
            filedescs=filedescs,
        )

        self.emitfunc('livedata', params)

    def notifyFitCurve(self, dataset, title, xvalues, yvalues):
        self.emitfunc('datacurve', (title, xvalues, yvalues))

    def breakpoint(self, level):
        exec(self._bpcode[level])

    def breakCallback(self, break_arg, iteration):
        """Will be called every 60 seconds while the script is paused."""
        # repeat user prompts
        if self._user_prompt:
            self.emitfunc('prompt', self._user_prompt)
        # notify by email once after 10 minutes and then every 30 minutes
        if iteration == PAUSE_NOTIFICATION_INTERVAL or \
           iteration % (3*PAUSE_NOTIFICATION_INTERVAL) == 0:
            self.notify('NICOS still paused',
                        f'A NICOS script is still paused, by {break_arg[2]}. '
                        'Please check if it can be continued.',
                        what='pause reminder')

    def pause(self, prompt, inputcmd=None):
        self.daemon_device._controller.set_break(
            ('break', BREAK_NOW, 'pause()'))
        self._user_prompt = (prompt, str(uuid1()))
        self.emitfunc('prompt', self._user_prompt)
        self.breakpoint(3)
        self.emitfunc('promptdone', (self._user_prompt[1],))
        self._user_prompt = None

    def userinput(self, prompt, validator=str, default=Ellipsis):
        self.daemon_device._controller.set_break(
            ('break', BREAK_NOW, 'userinput()'))
        self._user_prompt = (prompt, str(uuid1()), validator, default)
        self.emitfunc('prompt', self._user_prompt)
        # Must be set by the client by calling setUserinput
        self._user_input = Ellipsis
        self.breakpoint(3)
        self.emitfunc('promptdone', (self._user_prompt[1],))
        self._user_prompt = None
        return self._user_input

    def setUserinput(self, uid, value):
        if self._user_prompt and uid == self._user_prompt[1]:
            self._user_input = value

    def checkAccess(self, required):
        if 'level' in required:
            script = self.daemon_device.current_script()
            rlevel = required['level']
            if isinstance(rlevel, str):
                for k, v in ACCESS_LEVELS.items():
                    if v == rlevel:
                        rlevel = k
                        break
                else:
                    raise AccessError('invalid access level name: %r' % rlevel)
            if script and rlevel > script.user.level:
                raise AccessError('%s access is not sufficient, %s access '
                                  'is required' % (
                                      ACCESS_LEVELS.get(script.user.level,
                                                        str(script.user.level)),
                                      ACCESS_LEVELS.get(rlevel, str(rlevel))))
        return NoninteractiveSession.checkAccess(self, required)

    def checkParallel(self):
        return self.script_thread_id and \
            self.script_thread_id != threading.current_thread().ident

    def showHelp(self, obj=None):
        try:
            data = self._helper.generate(obj)
        except ValueError:
            self.log.info('Sorry, no help exists for %r.', obj)
            return
        except Exception:
            self.log.warning('Could not generate the help for %r', obj, exc=1)
            return
        if not isinstance(obj, str):
            self.log.info('Showing help in the calling client...')
        self.emitfunc_private('showhelp', data)

    def getExecutingUser(self):
        return self.daemon_device.current_user()

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

    def pnpEvent(self, event, setupname, description):
        # not calling parent function as we do not want logging
        self.emitfunc('plugplay', (event, setupname, description))

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

    def watchdogEvent(self, event, time, data, entry_id):
        """Handle a watchdog alarm event."""
        if event == 'warning':
            self.log.warning('WATCHDOG ALERT: %s', data)
        self.emitfunc('watchdog', (event, time, data, entry_id))

    def abortScript(self):
        raise ControlStop('', '', 'abort()')
