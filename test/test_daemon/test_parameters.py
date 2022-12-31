#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krüger@frm2.tum.de>
#
# *****************************************************************************

from nicos.services.daemon.auth.ldap import ldapuri

from test.utils import raises


def test_ldapuri():
    assert ldapuri('localhost') == 'localhost'
    assert ldapuri('ldap://localhost') == 'ldap://localhost'
    assert ldapuri('ldaps://localhost') == 'ldaps://localhost'

    assert ldapuri('example.host.my') == 'example.host.my'
    assert ldapuri('ldap://example.host.my') == 'ldap://example.host.my'
    assert ldapuri('ldaps://example.host.my') == 'ldaps://example.host.my'
    assert ldapuri('ldap://localhost:3389') == 'ldap://localhost:3389'
    assert ldapuri('ldaps://localhost:6636') == 'ldaps://localhost:6636'
    assert ldapuri('ldap://localhost:3389/') == 'ldap://localhost:3389/'
    assert ldapuri('ldaps://localhost:6636/') == 'ldaps://localhost:6636/'

    assert raises(ValueError, ldapuri, 'lda://localhost')
    assert raises(ValueError, ldapuri, 'ldap//localhost')
    assert raises(ValueError, ldapuri, 'ldap:/localhost')
    assert raises(ValueError, ldapuri, 'ldap:localhost')
    assert raises(ValueError, ldapuri, 'ldap://loca lhost')
    assert raises(ValueError, ldapuri, 'ldap://localhost ')
    assert raises(ValueError, ldapuri, ' ldap://localhost ')
