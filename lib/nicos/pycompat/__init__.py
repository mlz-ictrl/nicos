#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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

"""Python 2/3 compatibility."""

__all__ = [
    'builtins',
    'OrderedDict', 'get_thread_id'
]

import threading

# Pylint cannot handle submodules created by "six".  Import them here to
# ignore the Pylint errors only once.
from six.moves import builtins  # pylint: disable=F0401

try:
    from collections import OrderedDict  # pylint: disable=E0611
except ImportError:
    from ordereddict import OrderedDict

try:
    get_thread_id = threading._get_ident
except AttributeError:
    get_thread_id = threading.get_ident
