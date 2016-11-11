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

"""Module for output/logging user commands."""

from nicos import session
from nicos.commands import usercommand, hiddenusercommand, helparglist, \
    parallel_safe


__all__ = [
    'printdebug', 'printinfo', 'printwarning', 'printerror', 'printexception',
]


def _convertargs(msgs):
    # backward compatibility helper, can be removed once printinfo() is
    # switched to normal logging behavior
    if len(msgs) > 1 and '%s' not in msgs[0]:
        return (msgs[0] + ' %s' * (len(msgs) - 1),) + msgs[1:]
    return msgs


@hiddenusercommand
@helparglist('message, ...')
@parallel_safe
def printdebug(*msgs, **kwds):
    """Print a debug message."""
    session.log.debug(*_convertargs(msgs), **kwds)


@usercommand
@helparglist('message, ...')
@parallel_safe
def printinfo(*msgs, **kwds):
    """Print a message.

    This function is equivalent to the standard Python "print" statement.
    """
    session.log.info(*_convertargs(msgs), **kwds)


@usercommand
@helparglist('message, ...')
@parallel_safe
def printwarning(*msgs, **kwds):
    """Print a warning message.

    In the output history, the message will be highlighted as a warning and
    therefore be more visible than normal "info" messages.

    Example:

    >>> printwarning('count rate < 1000 Hz')
    """
    session.log.warning(*_convertargs(msgs), **kwds)


@usercommand
@helparglist('message, ...')
@parallel_safe
def printerror(*msgs):
    """Print an error message.

    In the output history, the message will be highlighted as an error (usually
    in red and bold) and therefore be very visible.

    Example:

    >>> printerror('scan failed, repeating this run')
    """
    session.log.error(*_convertargs(msgs))


@hiddenusercommand
@helparglist('message, ...')
@parallel_safe
def printexception(*msgs):
    """Print an error message, and add info about the last exception."""
    session.log.exception(*_convertargs(msgs))
