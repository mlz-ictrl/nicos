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

"""Session classes for simple and noninteractive use."""

from __future__ import print_function

import sys
import signal

from nicos import session
from nicos.utils import daemonize, setuser, writePidfile, removePidfile
from nicos.core.sessions import Session
from nicos.core import SLAVE
from nicos.pycompat import exec_


class NoninteractiveSession(Session):
    """
    Subclass of Session that configures the logging system for simple
    noninteractive usage.
    """

    autocreate_devices = False

    def _beforeStart(self, maindev):
        pass

    @classmethod
    def _get_maindev(cls, appname, maindevname, setupname):
        session.loadSetup(setupname or appname, allow_special=True,
                          raise_failed=True, autoload_system=False)
        return session.getDevice(maindevname or appname.capitalize())

    @classmethod
    def run(cls, appname, maindevname=None, setupname=None, pidfile=True,
            daemon=False, start_args=None):
        if daemon:
            daemonize()
        else:
            setuser()

        def quit_handler(signum, frame):
            maindev.quit(signum=signum)

        def reload_handler(signum, frame):
            if hasattr(maindev, 'reload'):
                maindev.reload()

        def status_handler(signum, frame):
            if hasattr(maindev, 'statusinfo'):
                maindev.statusinfo()

        session.__class__ = cls
        try:
            session.__init__(appname, daemonized=daemon)
            maindev = cls._get_maindev(appname, maindevname, setupname)

            signal.signal(signal.SIGINT, quit_handler)
            signal.signal(signal.SIGTERM, quit_handler)
            if hasattr(signal, 'SIGUSR1'):
                signal.signal(signal.SIGUSR1, reload_handler)
                signal.signal(signal.SIGUSR2, status_handler)

            if pidfile:
                writePidfile(appname)

            session._beforeStart(maindev)
        except Exception as err:
            try:
                session.log.exception('Fatal error while initializing')
            finally:
                print('Fatal error while initializing:', err, file=sys.stderr)
            return 1

        start_args = start_args or ()
        maindev.start(*start_args)
        maindev.wait()

        session.shutdown()
        removePidfile(appname)


class SingleDeviceSession(NoninteractiveSession):

    @classmethod
    def _get_maindev(cls, appname, maindevcls, setup):
        return maindevcls(appname, **setup)


class ScriptSession(Session):
    """
    Subclass of Session that allows for batch execution of scripts.
    """

    has_datamanager = True

    @classmethod
    def run(cls, setup, code, mode=SLAVE, appname='script'):
        session.__class__ = cls

        try:
            session.__init__(appname)
        except Exception as err:
            try:
                session.log.exception('Fatal error while initializing')
            finally:
                print('Fatal error while initializing:', err, file=sys.stderr)
            return 1

        # Load the initial setup and handle becoming master.
        session.handleInitialSetup(setup, mode)

        # Execute the script code and shut down.
        exec_(code, session.namespace)
        session.shutdown()
