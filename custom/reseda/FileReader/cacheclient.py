#!/usr/bin/env python
#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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
import os.path

loggerFormat = '[%(asctime)s][%(levelname)s]: %(message)s'
logging.basicConfig(format=loggerFormat)
logging.getLogger().setLevel(logging.INFO)


class SimpeCacheClient(object):
    def __init__(self, host, port, prefix=''):
        self._prefix = prefix

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.connect((host, port))

    def setKey(self, key, value):

        if self._prefix:
            key = '%s/%s' % (self._prefix, key)

        logging.info('Set key: %s => %s' % (key, str(value)))

        self.__write('%s=%s' % (key, str(value)))

    def readKey(self, key):

        if self._prefix:
            key = '%s/%s' % (self._prefix, key)

        logging.info('Read key: %s' % key)

        self.__write('%s?' % key)
        response = self.__read('%s?' % key)
        value = response.split('=')[1]

        logging.info('\t=> %s' % value)

        return value

    def __write(self, msg):
        fullMsg = '%s\n' % msg

        logging.debug('Write: %s' % fullMsg.encode('string-escape'))

        self._socket.send(fullMsg)

    def __read(self, msg):
        response = self._socket.recv(1024)[:-1]

        logging.debug('Read: %s' % response)

        return response

class FileToCache(object):
    def __init__(self, host, port):
        self._cache = SimpeCacheClient(host, port, 'nicos')


    def sendFileToCache(self, dataFile):
        with open(dataFile, 'r') as f:
            for line in f:
                tmp = line.strip().split('\t')
                if len(tmp) >= 2:
                    self._cache.setKey(tmp[0], tmp[1])




function = FileToCache('localhost', 14869)	##Hostname vom Linux-Pc
fileDir = os.path.dirname(__file__)
dataFile = os.path.join(fileDir, 'data.txt')

while True:
	function.sendFileToCache(dataFile)
	time.sleep(30)

