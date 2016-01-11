#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
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

"""Session used for the NICOS web interface."""

import sys
from wsgiref.simple_server import make_server

from nicos import session
from nicos.utils.loggers import INFO
from nicos.core.sessions import Session
from nicos.core.sessions.utils import LoggingStdout
from nicos.services.web.app import FakeInput, MTWSGIServer, NicosApp


class WebSession(Session):
    """
    Subclass of Session that configures the logging system for usage in a web
    application environment.
    """

    def _initLogging(self, prefix=None, console=True):
        Session._initLogging(self, prefix, console)
        sys.displayhook = self._displayhook

    def _displayhook(self, value):
        if value is not None and getattr(value, '__display__', True):
            self.log.log(INFO, repr(value))

    @classmethod
    def run(cls, setup='startup'):
        sys.stdin = FakeInput()

        session.__class__ = cls
        session.__init__('web')

        app = NicosApp()
        session.createRootLogger()
        session.log.addHandler(app.create_loghandler())
        sys.stdout = LoggingStdout(sys.stdout)

        session.loadSetup(setup)

        srv = make_server('', 4000, app, MTWSGIServer)
        session.log.info('web server running on port 4000')
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            session.log.info('web server shutting down')
