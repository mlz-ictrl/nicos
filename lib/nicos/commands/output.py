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

"""Module for output/logging user commands."""

__version__ = "$Revision$"

from nicos import session
from nicos.commands import usercommand, hiddenusercommand, helparglist


@hiddenusercommand
@helparglist('message, ...')
def printdebug(*msgs, **kwds):
    """Print a debug message."""
    session.log.debug(*msgs, **kwds)

@usercommand
@helparglist('message, ...')
def printinfo(*msgs, **kwds):
    """Print a message."""
    session.log.info(*msgs, **kwds)

@usercommand
@helparglist('message, ...')
def printwarning(*msgs, **kwds):
    """Print a warning message."""
    session.log.warning(*msgs, **kwds)

@usercommand
@helparglist('message, ...')
def printerror(*msgs):
    """Print an error message."""
    session.log.error(*msgs)

@hiddenusercommand
@helparglist('message, ...')
def printexception(*msgs):
    """Print an error message, and add info about the last exception."""
    session.log.exception(*msgs)
