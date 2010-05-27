#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS output/logging user commands
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

"""Module for output/logging user commands."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from nicm import nicos

__commands__ = [
    'printdebug', 'printinfo', 'printwarning', 'printerror', 'printexception',
]


def printdebug(*msgs, **kwds):
    nicos.log.debug(*msgs, **kwds)

def printinfo(*msgs, **kwds):
    nicos.log.info(*msgs, **kwds)

def printwarning(*msgs, **kwds):
    nicos.log.warning(*msgs, **kwds)

def printerror(*msgs):
    nicos.log.error(*msgs)

def printexception(*msgs):
    nicos.log.exception(*msgs)
