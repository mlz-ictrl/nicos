#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************
"""Classes to handle the setup files."""

import redbaron


class DaemonSetup(object):
    """Class to handle the daemon setup file."""

    def __init__(self, filename):
        self._filename = filename

        with open(filename) as f:
            self.setup = redbaron.RedBaron(f.read())

        # search for the list authenticator entries
        # pylint: disable=not-callable
        auth = self.setup('string',
                          value="'nicos.services.daemon.auth.ListAuthenticator'")
        # and take the first one
        # from the found string value we have to find the device entry
        self.passwd = None
        self.hashing = 'sha1'
        if auth:
            auth = auth[0].parent.parent.parent.parent
            # find the password entry inside the device entry
            # self.passwd = auth.value.value[1]('callargument',
            self.passwd = auth('callargument',
                               target=lambda x: str(x) == 'passwd')[0].value
            self.hashing = auth('callargument',
                                target=lambda x: str(x) == 'hashing')[0]

    def getPasswordEntries(self):
        """Return the password entry list.

        All entries will be converted to strings. If the password field
        contains the hashlib call it will generate a NameError which will be
        catched so the entry will not converted to the hexdigest
        """
        if not self.passwd:
            return []
        passwd = []
        pwtuple = self.passwd.value('tuple')
        for pw in pwtuple:
            v1, v2, v3 = str(pw.value[0]), str(pw.value[1]), str(pw.value[2])
            try:
                # the order is important, the v2 must be check last since it
                # may contain the 'hashlib' call, which should not be changed
                v1 = eval(v1)
                v3 = eval(v3)
                v2 = eval(v2)
            except NameError:
                pass
            passwd.append((v1, v2, v3))
        return passwd

    def getHashing(self):
        """Return the password hashing algorithm type."""
        return eval(str(self.hashing.value))

    def setHashing(self, hashing):
        """Set the new hashing algorithm type."""
        if hashing in ['md5', 'sha1']:
            self.hashing.value = '%r' % hashing

    def updatePasswordEntries(self, passwd):
        """Update the password entry in setup file.

        The list of password entries will be updated. The formatting checks
        for hash values and formats the output corresponding to the setup file
        syntax.
        """
        if not isinstance(passwd, list) or self.passwd is None:
            return
        del self.passwd.value[:]
        passwd.sort(key=lambda x: (1 if x[2] == 'guest' else 2
                    if x[2] == 'user' else 3, x[1]))
        for user, pwhash, role in passwd:
            fmtstr = '(%r, %r, %r)'
            try:
                # check if is it a hashlib call
                if redbaron.RedBaron(pwhash):
                    fmtstr = '(%r, %s, %r)'
            except:  # pylint: disable=bare-except
                pass
            pwentry = fmtstr % (user, pwhash, role)
            self.passwd.value.append(pwentry)

    def save(self):
        """Write the setup content to file."""
        with open(self._filename, 'w') as f:
            f.write(self.setup.dumps())
