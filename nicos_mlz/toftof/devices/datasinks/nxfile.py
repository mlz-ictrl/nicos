#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

#
# Parts of the  code for the NexusFile class were taken from the
# nexusformat.nexus.tree implementation of the NeXpy project and modified to
# write the data (esp. string data) in a NeXus API compatible way.
#

# Copyright (c) 2013-2016, NeXpy Development Team.
#
# Author: Paul Kienzle, Ray Osborn
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.bsd, distributed with this software.

from __future__ import absolute_import, division, print_function

import os

import numpy as np
from nexusformat.nexus import NeXusError, NXfield, NXlink
from nexusformat.nexus.tree import is_text

import nxs

# import h5py as h5

__all__ = ('NexusFile',)


class NexusFile(object):
    """Structure-based interface to write a NeXus API compatible file.

    Since the NeXus API library may only read HDF5 files with fixed length of
    strings the NXFile class from the tree library does not work with tools
    like Mantid.

    The writing uses the Python bindings of the NeXus API.

    Parts of the codes are taken from the tree implementation of the NXFile
    class.

    Usage::

      file = NeXusFile(filename, ['r','rw','w'])
        - open the NeXus file
      file.writefile(root)
        - write a NeXus tree to the file.

    Example::

      nx = NXFile('REF_L_1346.nxs','r')
      nx.writefile(tree)
    """

    def __init__(self, name, mode='r', **kwds):
        """Create a Nexus File object for reading and writing."""
        self._file = None
        name = os.path.abspath(name)
        self.name = name
        if mode == 'w4' or mode == 'wx':
            raise NeXusError('Only HDF5 files supported')
        elif mode == 'w' or mode == 'w-' or mode == 'w5':
            if mode == 'w5':
                mode = 'w'
            self._mode = 'rw'
            self._file = nxs.open(name, 'w5')
        else:
            if mode == 'rw' or mode == 'r+':
                self._mode = 'rw'
                mode = 'r+'
            else:
                self._mode = 'r'
            self._file = nxs.open(name, 'w5')
        self._filename = self._file.filename
        self._path = '/'

    def __repr__(self):
        return '<NXFile "%s" (mode %s)>' % (os.path.basename(self._filename),
                                            self._mode)

    def __enter__(self):
        return self.open()

    def __exit__(self, *args):
        self.close()

    def open(self, **kwds):
        if not self.isopen():
            if self._mode == 'rw':
                self._file = nxs.open(self._filename, 'w5')
            else:
                self._file = nxs.open(self._filename, 'w5')
            self.nxpath = '/'
        return self

    def close(self):
        if self.isopen():
            self._file.close()
        self._file = None

    def isopen(self):
        return self._file

    def writefile(self, tree):
        """Write the NeXus structure to a file.

        The file is assumed to start empty.
        """
        links = []
        self.nxpath = ''
        for entry in tree.values():
            links += self._writegroup(entry)
        self._writelinks(links)
        if tree.attrs:
            self._writeattrs(tree.attrs)

    def _writeattrs(self, attrs):
        """Write the attributes for the group/data with the current path.

        Null attributes are ignored.
        """
        # pylint: disable=len-as-condition
        for name, value in attrs.items():
            if is_text(value.nxdata):
                self._file.putattr(name, str(value))
            else:
                if isinstance(value.nxdata, (int, float)) or len(value.nxdata):
                    self._file.putattr(name, value.nxdata, value.dtype)

    def _writegroup(self, group):
        """Write the given group structure, including the data.

        Internal NXlinks cannot be written until the linked group is created,
        so this routine returns the set of links that need to be written.
        Call writelinks on the list.
        """
        if group.nxpath and group.nxpath != '/':
            self.nxpath = self.nxpath + '/' + group.nxname
            try:
                self._file.opengrouppath(self.nxpath)
            except Exception:
                self._file.makegroup(group.nxname, group.nxclass)
        links = []
        self._writeattrs(group.attrs)
        if group._target is not None:
            links += [(self.nxpath, group._target)]
        for child in group.values():
            if isinstance(child, NXlink):
                if child._filename is not None:
                    self._writeexternal(child)
                else:
                    links += [(self.nxpath + '/' + child.nxname,
                               child._target)]
            elif isinstance(child, NXfield):
                links += self._writedata(child)
            else:
                links += self._writegroup(child)
        self.nxpath = self.nxparent
        if self._file.path != '/':
            self._file.closegroup()
        return links

    def _writedata(self, data):
        """Write the given data to a file.

        NXlinks cannot be written until the linked group is created, so
        this routine returns the set of links that need to be written.
        Call writelinks on the list.
        """
        self._file.opengrouppath(self.nxpath)
        try:
            self._file.opendata(data.nxname)
        except ValueError:
            dlen = list(data.shape) if data.shape else [1]
            if is_text(data.nxdata):
                dlen = [len(data.nxdata)]
                self._file.makedata(data.nxname, 'char', dlen)
            else:
                if np.prod(data.shape) > 10000:
                    if not data._compression:
                        data._compression = 'lzw'
                if data._compression and isinstance(data, np.ndarray) and \
                   data._value.sum() > 0:
                    self._file.compmakedata(data.nxname, data.dtype,
                                            data.shape, data._compression,
                                            [data.shape[0], data.shape[1],
                                             data.shape[0] / 50.
                                             ])
                else:
                    self._file.makedata(data.nxname, data.dtype, dlen)
            self._file.opendata(data.nxname)
        self.nxpath = self.nxpath + '/' + data.nxname
        # If the data is linked then
        if data._target is not None:
            path = self.nxpath
            self.nxpath = self.nxparent
            return [(path, data._target)]
        elif data.dtype is not None:
            self._file.putdata(data._value)
        self._writeattrs(data.attrs)
        self.nxpath = self.nxparent
        self._file.closedata()
        return []

    def _writelinks(self, links):
        """Create links within the NeXus file.

        These are defined by the set of pairs returned by _writegroup.
        """
        # link sources to targets
        for path, target in links:
            if path != target:
                try:
                    self._file.opengrouppath(target)
                    targetID = self._file.getgroupID()
                except Exception:
                    tmp = target.split('/')
                    target = '/'.join(tmp[:-1])
                    self._file.opengrouppath(target)
                    self._file.opendata(tmp[-1])
                    targetID = self._file.getdataID()
                try:
                    self._file.opengrouppath(path)
                except Exception:
                    tmp = path.split('/')
                    target = '/'.join(tmp[:-1])
                    self._file.opengrouppath(target)
                self._file.makelink(targetID)

    @property
    def filename(self):
        """File name on disk."""
        return self._filename

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode):
        if mode == 'rw' or mode == 'r+':
            self._mode = 'rw'
            if self.isopen() and self._mode == 'r':
                self.close()
        else:
            self._mode = 'r'
            if self.isopen() and self._mode == 'r+':
                self.close()

    @property
    def nxparent(self):
        return '/' + self.nxpath[:self.nxpath.rfind('/')].lstrip('/')
