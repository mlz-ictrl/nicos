#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   Standard NICOS exceptions
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""Exception classes for usage in NICOS."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"



class NicmError(Exception):
    category = 'Error'
    device = None

    def __init__(self, *args):
        # store the originating device on the exception
        from nicm.device import Device
        args = list(args)
        if args and isinstance(args[0], Device):
            self.device = args[0]
            args[0] = args[0].name + ': '
        Exception.__init__(self, ''.join(args))


class ProgrammingError(NicmError):
    category = 'NICOS bug'

class ConfigurationError(NicmError):
    category = 'Configuration error'

class UsageError(NicmError):
    category = 'Usage error'

class PositionError(NicmError):
    category = 'Position error'

class MoveError(NicmError):
    category = 'Positioning error'

class LimitError(NicmError):
    category = 'Out of bounds'

class FixedError(NicmError):
    category = 'Device fixed'

class CommunicationError(NicmError):
    category = 'Communication error'

class TimeoutError(CommunicationError):
    category = 'Timeout'
