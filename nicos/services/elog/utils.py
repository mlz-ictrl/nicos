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
#
# *****************************************************************************

"""Utilities for the electronic logbook daemon."""

import time
from cgi import escape
from logging import DEBUG, INFO, WARNING, ERROR, FATAL

from nicos.utils.loggers import INPUT, ACTION


levels = {DEBUG: 'DEBUG', INFO: 'INFO', WARNING: 'WARNING',
          ERROR: 'ERROR', FATAL: 'FATAL', INPUT: 'INPUT'}


def formatTime(timeval):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timeval))


def formatMessage(message):
    """Format message for display in the HTML logbook."""
    cls = 'out'
    levelno = message[2]
    if levelno == ACTION:
        return ''
    if message[0] == 'nicos':
        name = ''
    else:
        name = '%-10s: ' % message[0]
    name = message[5] + name
    if levelno <= DEBUG:
        text = name + message[3]
        cls = 'debug'
    elif levelno <= INFO:
        text = name + message[3]
    elif levelno == INPUT:
        return '<span class="input">' + escape(message[3]) + '</span>'
    elif levelno <= WARNING:
        text = levels[levelno] + ': ' + name + message[3]
        cls = 'warn'
    else:
        text = '%s [%s] %s%s' % (levels[levelno], formatTime(message[1]),
                                 name, message[3])
        cls = 'err'
    return '<span class="%s">%s</span>' % (cls, escape(text))


def formatMessagePlain(message):
    """Format message for the plain-text log file."""
    levelno = message[2]
    if levelno == ACTION:
        return ''
    # note: message will already contain newline at the end
    return '%s : %-7s : %s: %s' % (formatTime(message[1]),
                                   levels[levelno], message[0], message[3])


def pretty1(fmtstr, value):
    try:
        return fmtstr % value
    except (ValueError, TypeError):
        return str(value)


def pretty2(fmtstr, value1, value2):
    fmt1 = pretty1(fmtstr, value1)
    fmt2 = pretty1(fmtstr, value2)
    if fmt1 == fmt2:
        return fmt1
    if value1 is not None and value2 is not None:
        if value1 != 0 and abs((value2 - value1)/value1) < 0.00001:
            return fmt2
        if value2 != 0 and abs((value2 - value1)/value2) < 0.00001:
            return fmt1
    return '%s - %s' % (fmt1, fmt2)
