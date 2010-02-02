#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS device status code definitions
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   $Author$
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

"""
Status code definitions.
"""

# this doesn't use smaller values to avoid collision with old-style
# statuslist values that may be defined differently; this way they will
# raise a clear error instead when used
OK = 100
BUSY = 101
ERROR = 102
PAUSED = 103
UNKNOWN = 999

# dictionary mapping all status constants to their names
statuses = dict((v, k.lower()) for (k, v) in globals().iteritems()
                if isinstance(v, int))
