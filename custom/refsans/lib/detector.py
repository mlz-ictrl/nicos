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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Special device for Refsans Fast Detector (Comtec p7888)"""


from Detector import Detector
from IO import Counter

from nicos.core import Param, Value, Override, oneof, Value, ArrayDesc, ImageSink
from nicos.devices.generic.detector import PassiveChannel, ActiveChannel, \
    TimerChannelMixin, CounterChannelMixin, ImageChannelMixin
from nicos.devices.taco.detector import BaseChannel

import numpy as np

class ComtecCounter(CounterChannelMixin, BaseChannel, PassiveChannel):
    taco_class = Counter

    parameter_overrides = {
        'type' : Override(type=oneof('counter'), mandatory=False, default='counter'),
        'mode' : Override(type=oneof('normal'), mandatory=False, default='normal'),
        'fmtstr' : Override(default='%d'),
    }

    def doReadMode(self):
        return 'normal'

    def doWriteMode(self, value):
        return 'normal'

    def doReadIsmaster(self):
        return False

    def doWriteIsmaster(self, value):
        return False

    def valueInfo(self):
        return Value(self.name, unit='cts', errors='sqrt',
                     type='counter', fmtstr='%d'),

class ComtecTimer(TimerChannelMixin, BaseChannel, ActiveChannel):
    taco_class = Detector

    parameters = {
        'binwidth' : Param('Binning of timing channels', type=int, settable=True, chatty=True),
        'range' : Param('timing range', type=int, settable=True, chatty=True),
        'prefix': Param('Prefix of datafiles to be written', type=str, settable=True, chatty=True),
        'writelist': Param('write listfile?', type=oneof(True, False), settable=True, chatty=True),
        'autoinc': Param('auto-inc prefix?', type=oneof(True, False), settable=True, chatty=True),
        'autosave': Param('auto-save?', type=oneof(True, False), settable=True, chatty=True),
    }

    def doRead(self, maxage=0):
        return self._taco_guard(self._dev.read)[3]*0.001

    def doReadIsmaster(self):
        return True

    def doWriteIsmaster(self, value):
        return True # is ALWAYS master

    def doReadBinwidth(self):
        return int(self._taco_guard(self._dev.deviceQueryResource, 'binwidth')[:-1])

    def doWriteBinwidth(self, value):
        self.doStop()
        self._taco_guard(self._dev.deviceOff)
        self._taco_guard(self._dev.deviceUpdateResource, 'binwidth', '%dL' % value)
        self._taco_guard(self._dev.deviceOn)

    def doReadRange(self):
        return int(self._taco_guard(self._dev.deviceQueryResource, 'range')[:-1])

    def doWriteRange(self, value):
        self.doStop()
        self._taco_guard(self._dev.deviceOff)
        self._taco_guard(self._dev.deviceUpdateResource, 'range', '%dL' % value)
        self._taco_guard(self._dev.deviceOn)

    def doReadPrefix(self):
        return self._taco_guard(self._dev.deviceQueryResource, 'prefix')

    def doWritePrefix(self, value):
        self.doStop()
        self._taco_guard(self._dev.deviceOff)
        self._taco_guard(self._dev.deviceUpdateResource, 'prefix', '%s' % value)
        self._taco_guard(self._dev.deviceOn)

    def doReadWritelist(self):
        return self._taco_guard(self._dev.deviceQueryResource, 'writelist').lower() != 'off'

    def doWriteWritelist(self, value):
        self.doStop()
        self._taco_guard(self._dev.deviceOff)
        self._taco_guard(self._dev.deviceUpdateResource, 'writelist', 'On' if value else 'Off')
        self._taco_guard(self._dev.deviceOn)

    def doReadAutoinc(self):
        return self._taco_guard(self._dev.deviceQueryResource, 'autoinc').lower() != 'off'

    def doWriteAutoinc(self, value):
        self.doStop()
        self._taco_guard(self._dev.deviceOff)
        self._taco_guard(self._dev.deviceUpdateResource, 'autoinc', 'On' if value else 'Off')
        self._taco_guard(self._dev.deviceOn)

    def doReadAutosave(self):
        return self._taco_guard(self._dev.deviceQueryResource, 'autosave').lower() != 'off'

    def doWriteAutosave(self, value):
        self.doStop()
        self._taco_guard(self._dev.deviceOff)
        self._taco_guard(self._dev.deviceUpdateResource, 'autosave', 'On' if value else 'Off')
        self._taco_guard(self._dev.deviceOn)

    def valueInfo(self):
        return Value(self.name, unit='s', errors='next',
                     type='time', fmtstr='%d'),

class ComtecFilename(BaseChannel, PassiveChannel):
    taco_class = Detector

    def doRead(self, maxage=0):
        return self._taco_guard(self._dev.deviceQueryResource, 'prefix') # How to obtain the part after the prefix???

    def doReadIsmaster(self):
        return False

    def doWriteIsmaster(self, value):
        return False # is NEVER master

    def valueInfo(self):
        return Value(self.name, unit='', errors='none',
                     type='filename', fmtstr='%s'),


class NullImage(ImageChannelMixin, PassiveChannel):
    arraydesc = ArrayDesc('', (1, 1), np.uint32)
    def readFinalImage(self):
        return np.zeros((1, 1), dtype='uint32')



class ComtecFileFormat(ImageSink):
    """Saves RAW image and header data into a single file"""
    parameter_overrides = {
        'filenametemplate': Override(mandatory=False, settable=False,
                                     userparam=False,
                                     default=['%(proposal)s_%(counter)s.cfg',
                                              '%(proposal)s_%(session.experiment.lastscan)s'
                                              '_%(counter)s_%(scanpoint)s.cfg']),
    }

    fileFormat = 'ComtecSingleRAW'     # should be unique amongst filesavers!

    # no need to define prepareImage and finalizeImage, as they do already
    # all we need

    def acceptImageType(self, imagetype):
        # everything can be saved RAW
        return True

    def updateImage(self, imageinfo, image):
        """just write the raw data upon update"""
        # XXX: copy over data from comtec fs exort
        #~ imageinfo.file.seek(0)
        #~ imageinfo.file.write(np.array(image).tostring())
        #~ imageinfo.file.flush()

    def _writeCFGHeader(self, imagetype, header, fp):
        fp.seek(0)
        fp.write('[NICOS2_Header]\n')
        fp.flush()

    def _writeHeader(self, imagetype, header, fp):
        fp.write('\n### NICOS %s File Header V2.0\n' % self.fileFormat)
        for category, valuelist in sorted(header.items()):
            if valuelist:
                fp.write('### %s\n' % category)
            for (dev, key, value) in valuelist:
                fp.write('%25s : %s\n' % ('%s_%s' % (dev.name, key), value))
        # to ease interpreting the data...
        fp.write('\n%r\n' % imagetype)
        fp.flush()

    def saveImage(self, imageinfo, image):
        self._writeCFGHeader(imageinfo.imagetype, imageinfo.header, imageinfo.file)
        self._writeHeader(imageinfo.imagetype, imageinfo.header, imageinfo.file)
        imageinfo.file.close()
