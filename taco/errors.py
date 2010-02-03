#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id $
#
# Description:
#   TACO <-> NICOS exception mapping
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

"""Utilities to map TACO errors to NICM errors."""

__author__  = "$Author$" 
__date__    = "$Date$"
__version__ = "$Revision$"

import sys

from TACOClient import TACOError

from nicm.errors import NicmError, CommunicationError


def taco_guard(function, *args):
    """Try running the TACO function, and raise a NicmError on exception."""
    try:
        return function(*args)
    except TACOError, err:
        raise_taco(err)


def raise_taco(err, addmsg=None):
    """Raise a suitable NicmError for a given TACOError instance."""
    tb = sys.exc_info()[2]
    code = err.errcode
    cls = NicmError
    if 401 <= code < 499:
        # error number 401-499: database system error messages
        cls = CommunicationError
    # TODO: add more cases
    msg = '[TACO %d] %s' % (err.errcode, err)
    if addmsg is not None:
        msg = addmsg + ': ' + msg
    raise cls(msg), None, tb
