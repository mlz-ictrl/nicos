#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICM cache client support
#
# Author:
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
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

"""NICM cache utils."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import re


DEFAULT_CACHE_PORT = 14869

# regular expression matching a cache protocol message
msg_pattern = re.compile(r'''
    ^ (?:
      \s* (?P<time>\d+\.?\d*)?    # timestamp
      \s* [+]?                    # ttl operator
      \s* (?P<ttl>\d+\.?\d*)?     # ttl
      \s* (?P<tsop>@)             # timestamp mark
    )?
    \s* (?P<key>[^=!?*]*?)        # key
    \s* (?P<op>[=!?*])            # operator
    \s* (?P<value>[^\r\n]*?)      # value
    \s* $
    ''', re.X)

line_pattern = re.compile(r'([^\r\n]*)(\r\n|\r|\n)')
