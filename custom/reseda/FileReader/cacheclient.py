#!/usr/bin/env python
#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#   Aleks Wischolit <aleks.wischolit@frm2.tum.de>
#
# *****************************************************************************

import socket
import logging
import time
from os import path

loggerFormat = '[%(asctime)s][%(levelname)s]: %(message)s'
logging.basicConfig(format=loggerFormat)
logging.getLogger().setLevel(logging.INFO)


class SimpleCacheClient(object):

    def __init__(self, host, port, prefix=''):
        self._prefix = prefix

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.connect((host, port))

    def setKey(self, key, value):

        if self._prefix:
            key = '%s/%s' % (self._prefix, key)

        logging.info('Set key: %s => %s', key, value)

        self.__write('%s=%s' % (key, str(value)))

    def readKey(self, key):

        if self._prefix:
            key = '%s/%s' % (self._prefix, key)

        logging.info('Read key: %s', key)

        self.__write('%s?' % key)
        response = self.__read('%s?' % key)
        value = response.split('=')[1]

        logging.info('\t=> %s', value)

        return value

    def __write(self, msg):
        fullMsg = '%s\n' % msg

        logging.debug('Write: %r', fullMsg)

        self._socket.send(fullMsg)

    def __read(self, msg):
        response = self._socket.recv(1024)[:-1]

        logging.debug('Read: %s', response)

        return response

class FileToCache(object):

    def __init__(self, host, port):
        self._cache = SimpleCacheClient(host, port, 'nicos')

    def sendFileToCache(self, dataFile):
        with open(dataFile, 'r') as f:
            for line in f:
                tmp = line.strip().split('\t')
                if len(tmp) >= 2:
                    self._cache.setKey(tmp[0], tmp[1])



## host name where the cache is running
cachehost = 'localhost'
# used cacheport
cacheport = 14869
# used data file
datafile = 'data.txt'

cw = FileToCache(cachehost, cacheport)
fileDir = path.dirname(__file__)
dataFile = path.join(fileDir, datafile)

def checker():
    if not path.isfile(dataFile):
        logging.warning('setup watcher could not find %s', dataFile)
        return
    mtime = path.getmtime(dataFile)
    while True:
        if path.getmtime(dataFile) != mtime:
            mtime = path.getmtime(dataFile)
            logging.info('data file changed: Push data to cache')
            cw.sendFileToCache(dataFile)
        time.sleep(1)

if __name__ == "__main__":
    checker()
