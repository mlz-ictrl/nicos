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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Tests for alias_config and alias preferences."""

from nicos import session


def setup_module():
    session.loadSetup('alias_config1', autocreate_devices=True)


def teardown_module():
    session.unloadSetup()


def test_alias_priorities():
    # normal session, only one choice
    T = session.getDevice('T')
    assert T.alias == 'T_ccr1'

    # load second setup, priority takes over
    session.loadSetup('alias_config2', autocreate_devices=True)
    T = session.getDevice('T')
    assert T.alias == 'T_cryo4'

    # now unload the setup that provides T_cryo4
    session.unloadSetup()
    session.loadSetup('alias_config1', autocreate_devices=True)
    T = session.getDevice('T')
    assert T.alias == 'T_ccr1'

    # load both at the same time, make sure higher priority wins
    session.unloadSetup()
    session.loadSetup(['alias_config2', 'alias_config1'], autocreate_devices=True)
    T = session.getDevice('T')
    assert T.alias == 'T_cryo4'
