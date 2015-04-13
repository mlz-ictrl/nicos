#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Andreas Schulz <andreas.schulz@frm2.tum.de>
#
# *****************************************************************************

from os import path


class ItemTypes(object):
    # used to distinguish QTreeWidgetItems
    Directory = 1200
    ManualDirectory = 1250
    Setup = 1300
    Device = 1400


def getNicosDir():
    # this file should be in */nicos-core/tools/setupfiletool/utilities
    return(path.abspath(path.join(path.dirname(__file__), '..', '..', '..')))


def getResDir():
    return(path.join(getNicosDir(), 'tools', 'setupfiletool', 'res'))
