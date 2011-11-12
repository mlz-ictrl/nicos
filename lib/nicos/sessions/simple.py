#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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

__version__ = "$Revision$"

import sys
import signal

from nicos import session
from nicos.utils import daemonize, setuser, writePidfile, removePidfile
from nicos.sessions import Session


class ScriptSession(Session):
    """
    Subclass of Session that allows for batch execution of scripts.
    """

    @classmethod
    def run(cls, setup, code):
        session.__class__ = cls

        try:
            session.__init__('script')
        except Exception, err:
            try:
                session.log.exception('Fatal error while initializing')
            finally:
                print >> sys.stderr, 'Fatal error while initializing:', err
            return 1

        # Load the initial setup and handle becoming master.
        session.handleInitialSetup(setup, False)

        # Execute the script code and shut down.
        exec code in session.getNamespace()
        session.shutdown()


class NoninteractiveSession(Session):
    """
    Subclass of Session that configures the logging system for simple
    noninteractive usage.
    """

    autocreate_devices = False
    auto_modules = []

    def _beforeStart(self, maindev):
        pass

    @classmethod
    def _get_maindev(cls, appname, maindevname, setupname):
        session.loadSetup(setupname or appname, allow_special=True,
                          raise_failed=True)
        return session.getDevice(maindevname or appname.capitalize())

    @classmethod
    def run(cls, appname, maindevname=None, setupname=None, pidfile=True,
            daemon=False, start_args=[]):

        if daemon:
            daemonize()
        else:
            setuser()

        session.__class__ = cls
        try:
            session.__init__(appname)
            maindev = cls._get_maindev(appname, maindevname, setupname)
        except Exception, err:
            try:
                session.log.exception('Fatal error while initializing')
            finally:
                print >> sys.stderr, 'Fatal error while initializing:', err
            return 1

        def quit_handler(signum, frame):
            removePidfile(appname)
            maindev.quit()
        def reload_handler(signum, frame):
            if hasattr(maindev, 'reload'):
                maindev.reload()
        def status_handler(signum, frame):
            if hasattr(maindev, 'statusinfo'):
                maindev.statusinfo()
        signal.signal(signal.SIGINT, quit_handler)
        signal.signal(signal.SIGTERM, quit_handler)
        signal.signal(signal.SIGUSR1, reload_handler)
        signal.signal(signal.SIGUSR2, status_handler)

        if pidfile:
            writePidfile(appname)

        session._beforeStart(maindev)

        maindev.start(*start_args)
        maindev.wait()

        session.shutdown()


class SingleDeviceSession(NoninteractiveSession):

    @classmethod
    def _get_maindev(self, appname, maindevcls, setup):
        return maindevcls(appname, **setup)
