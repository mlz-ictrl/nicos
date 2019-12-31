#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************
"""
This defines some commands for interfacing directly with EPICS from NICOS
This is for us, for debugging
"""
import epics

from nicos.commands import helparglist, hiddenusercommand


@hiddenusercommand
@helparglist('PV-name,optionaL as_string')
def caget(PV, as_string=True):
    return epics.caget(PV, as_string)


@hiddenusercommand
@helparglist('PV-name,value')
def caput(PV, value):
    return epics.caput(PV, value)


@hiddenusercommand
@helparglist('PV-name')
def cainfo(PV):
    return epics.cainfo(PV)
