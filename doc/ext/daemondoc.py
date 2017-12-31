#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

"""Directives to document daemon commands and events."""

import keyword
import inspect

from docutils.statemachine import ViewList
from sphinx.domains.python import PyModulelevel
from sphinx.util.docfields import Field
from sphinx.util.docstrings import prepare_docstring

from nicos.pycompat import getargspec
from nicos.services.daemon.handler import ConnectionHandler


class DaemonCommand(PyModulelevel):
    """Directive for daemon command description."""

    def handle_signature(self, sig, signode):
        if sig in keyword.kwlist:
            # append '_' to Python keywords
            self.object = getattr(ConnectionHandler, sig+'_')
        else:
            self.object = getattr(ConnectionHandler, sig)
        args = getargspec(self.object)
        del args[0][0]  # remove self
        sig = '%s%s' % (sig, inspect.formatargspec(*args))
        return PyModulelevel.handle_signature(self, sig, signode)

    def needs_arglist(self):
        return True

    def get_index_text(self, modname, name_cls):
        return '%s (daemon command)' % name_cls[0]

    def before_content(self):
        dstring = prepare_docstring(self.object.__doc__ or '')
        # overwrite content of directive
        self.content = ViewList(dstring)
        PyModulelevel.before_content(self)


class DaemonEvent(PyModulelevel):
    """Directive for daemon command description."""

    doc_field_types = [
        Field('arg', label='Argument', has_arg=False, names=('arg',)),
    ]

    def needs_arglist(self):
        return False

    def get_index_text(self, modname, name_cls):
        return '%s (daemon event)' % name_cls[0]


def setup(app):
    app.add_directive('daemoncmd', DaemonCommand)
    app.add_directive('daemonevt', DaemonEvent)
    return {'parallel_read_safe': True,
            'version': '0.1.0'}
