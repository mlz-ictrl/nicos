#  pylint: disable=unidiomatic-typecheck
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

"""Tests for the ftp upload module."""

import os
import tempfile
from io import BytesIO, StringIO

import pytest

from nicos.utils import createThread, ftp

try:
    from pyftpdlib.authorizers import DummyAuthorizer
    from pyftpdlib.filesystems import AbstractedFS
    from pyftpdlib.handlers import FTPHandler
    from pyftpdlib.servers import ThreadedFTPServer
except ImportError:
    ThreadedFTPServer = object
    FTPHandler = object
    AbstractedFS = object
    DummyAuthorizer = object


session_setup = None


class NamedBytesIO(BytesIO):
    def __init__(self, name):
        self.name = name
        BytesIO.__init__(self)

    def close(self):
        self.finalcontent = self.getvalue()
        return BytesIO.close(self)


class NamedStringIO(StringIO):
    def __init__(self, name):
        self.name = name
        StringIO.__init__(self)

    def close(self):
        self.finalcontent = self.getvalue()
        return StringIO.close(self)


class DataStorage:
    used_username = None
    ofilename = None
    omode = None
    iofile = None
    chdirpath = None
    mkdirpath = None


ds = DataStorage()


class FTPTestHandler(FTPHandler):
    ds = ds

    def on_login(self, username):
        self.ds.used_username = username
        return FTPHandler.on_login(self, username)


class MyTestFS(AbstractedFS):

    def open(self, filename, mode):
        """Overwritten to use in memory files"""
        self.cmd_channel.ds.ofilename = filename
        self.cmd_channel.ds.omode = mode
        if 'b' in mode:
            self.cmd_channel.ds.iofile = NamedBytesIO(filename)
        else:
            self.cmd_channel.ds.iofile = NamedStringIO(filename)
        return self.cmd_channel.ds.iofile

    def chdir(self, path):
        """Path changes are virtual"""
        if path in (self.cmd_channel.ds.mkdirpath, '/'):
            self.cmd_channel.ds.chdirpath = path
        return '/'

    def mkdir(self, path):
        """Do not create dirs."""
        self.cmd_channel.ds.mkdirpath = path


@pytest.fixture(scope='function')
def ftpserver():
    """Provide a ftp server with virtual files"""
    handler = FTPTestHandler
    handler.abstracted_fs = MyTestFS
    authorizer = DummyAuthorizer()
    home = os.curdir
    authorizer.add_user('user', '12345', home, perm='elrmwM')
    handler.authorizer = authorizer
    server = ThreadedFTPServer(('localhost', 12345), handler)

    createThread('FTP', server.serve_forever)
    yield handler
    server.close_all()


TEST_CONTENT = 'A test\n'


@pytest.fixture(scope='function')
def upload(session):
    """Provide a file to use as upload"""
    fd, t = tempfile.mkstemp(suffix='.txt')
    os.write(fd, TEST_CONTENT.encode())
    yield t
    os.unlink(t)


@pytest.mark.skipif(ThreadedFTPServer is object,
                    reason='pyftpdlib package not installed')
def test_ftp(session, ftpserver, upload):
    ftp.FTP_SERVER = 'localhost'
    ftp.FTP_PORT = 12345
    ftp.FTP_USER = 'user'
    ftp.FTP_P = '12345'

    ftp.ftpUpload(upload)
    assert ds.used_username == 'user'
    assert ds.ofilename
    assert ds.omode == 'wb'
    assert ds.iofile
    assert ds.iofile.finalcontent.decode() == TEST_CONTENT
    assert ds.mkdirpath
    assert ds.chdirpath
