#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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

import os
import shutil

import numpy as np

from IO import Counter
from Detector import Detector

from nicos import session
from nicos.core import Attach, Param, Value, Override, oneof, SIMULATION, \
    INFO_CATEGORIES, LIVE
from nicos.core.constants import POINT, SCAN
from nicos.core.data import DataSinkHandler
from nicos.devices.generic.detector import PassiveChannel, ActiveChannel, \
    TimerChannelMixin, CounterChannelMixin
from nicos.devices.taco.detector import BaseChannel as TacoBaseChannel
from nicos.devices.datasinks import ImageSink
from nicos.pycompat import iteritems
from nicos.utils import syncFile


class ComtecCounter(CounterChannelMixin, TacoBaseChannel, PassiveChannel):
    taco_class = Counter

    parameter_overrides = {
        'type':   Override(type=oneof('counter'), mandatory=False,
                           default='counter'),
        'mode':   Override(type=oneof('normal'), mandatory=False,
                           default='normal'),
        'fmtstr': Override(default='%d'),
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


class ComtecTimer(TimerChannelMixin, TacoBaseChannel, ActiveChannel):
    taco_class = Detector

    parameters = {
        'binwidth':  Param('Binning of timing channels', type=int,
                           settable=True, chatty=True),
        'range':     Param('Timing range', type=int, settable=True,
                           chatty=True),
        'prefix':    Param('Prefix of datafiles to be written', type=str,
                           settable=True, chatty=True),
        'writelist': Param('Write listfile?', type=bool,
                           settable=True, chatty=True),
        'autoinc':   Param('Auto-increment prefix?', type=bool, settable=True,
                           chatty=True),
        'autosave':  Param('Auto-save?', type=bool, settable=True,
                           chatty=True),
    }

    def doRead(self, maxage=0):
        return self._taco_guard(self._dev.read)[3] * 0.001

    def doReadIsmaster(self):
        return True

    def doWriteIsmaster(self, value):
        return True  # is ALWAYS master

    def doReadBinwidth(self):
        return int(self._taco_guard(self._dev.deviceQueryResource,
                                    'binwidth')[:-1])

    def doWriteBinwidth(self, value):
        self.doStop()
        self._taco_update_resource('binwidth', '%dL' % value)

    def doReadRange(self):
        return int(self._taco_guard(self._dev.deviceQueryResource,
                                    'range')[:-1])

    def doWriteRange(self, value):
        self.doStop()
        self._taco_update_resource('range', '%dL' % value)

    def doReadPrefix(self):
        return self._taco_guard(self._dev.deviceQueryResource, 'prefix')

    def doWritePrefix(self, value):
        self.doStop()
        self._taco_update_resource('prefix', str(value))

    def doReadWritelist(self):
        return self._taco_guard(self._dev.deviceQueryResource,
                                'writelist').lower() != 'off'

    def doWriteWritelist(self, value):
        self.doStop()
        self._taco_update_resource('writelist', 'On' if value else 'Off')

    def doReadAutoinc(self):
        return self._taco_guard(self._dev.deviceQueryResource,
                                'autoinc').lower() != 'off'

    def doWriteAutoinc(self, value):
        self.doStop()
        self._taco_update_resource('autoinc', 'On' if value else 'Off')

    def doReadAutosave(self):
        return self._taco_guard(self._dev.deviceQueryResource,
                                'autosave').lower() != 'off'

    def doWriteAutosave(self, value):
        self.doStop()
        self._taco_update_resource('autosave', 'On' if value else 'Off')

    def valueInfo(self):
        return Value(self.name, unit='s', errors='next',
                     type='time', fmtstr='%d'),


class ComtecFilename(TacoBaseChannel, PassiveChannel):
    taco_class = Detector

    def doRead(self, maxage=0):
        # How to obtain the part after the prefix???
        return self._taco_guard(self._dev.deviceQueryResource, 'prefix')

    def doReadIsmaster(self):
        return False

    def doWriteIsmaster(self, value):
        return False  # is NEVER master

    def valueInfo(self):
        return Value(self.name, unit='', errors='none',
                     type='filename', fmtstr='%s'),


class ComtecHeaderSinkHandler(DataSinkHandler):

    def prepare(self):
        # obtain filenames /prefixes
        # the first entry is normally used as the datafile.
        # we use it for the prefix of the det.
        # the other entries are normally 'just' the hardlinks to the datafile
        # we use the first for the filename and the others for the links.
        session.data.assignCounter(self.dataset)
        self.prefix, allfilepaths = session.data.getFilenames(
            self.dataset, self.sink.filenametemplate, self.sink.subdir)
        self.linkpaths = allfilepaths[1:]
        # set prefix on tacodevice
        self.sink._attached_detector.prefix = self.prefix
        self._arraydesc = self.detector.arrayInfo()[0]

    def putResults(self, quality, results):
        # write headerfile
        if quality == LIVE:
            return
        if self.detector.name in results:
            result = results[self.detector.name]
            if result is None:
                return
            image = result[1][0]
            self.log.debug("results: %r", results)
            self._file = session.data.createDataFile(
                self.dataset, [self.linkpaths[0] + self.prefix + '.header'],
                self.sink.subdir)
            self.writeHeader(self._file, self.dataset.metainfo, image)

    def writeHeader(self, fp, metainfo, image):
        fp.seek(0)
        fp.write(np.asarray(image).tostring())
        fp.write('\n### NICOS Raw File Header V2.0\n')
        fp.write('# detector prefix is %r' % self.prefix)
        bycategory = {}
        for (device, key), (_, val, unit, category) in iteritems(metainfo):
            if category:
                bycategory.setdefault(category, []).append(
                    ('%s_%s' % (device.name, key), (val + ' ' + unit).strip()))
        for category, catname in INFO_CATEGORIES:
            if category not in bycategory:
                continue
            fp.write('### %s\n' % catname)
            for key, value in sorted(bycategory[category]):
                fp.write('%25s : %s\n' % (key, value))
        # to ease interpreting the data...
        fp.write('\n%r\n' % self._arraydesc)
        fp.flush()

    def end(self):
        if self._file:
            self._file.close()
            syncFile(self._file)
            # datenfile aus dateisystem fieseln und kopieren. als self.linkpaths[0]
            # pattern is:
            # \home\pc\data2\A_username_JJJJ_MM\username_JJJJ_MM-xxx-A1-yyy.lst
            # \home\pc\data3\B_username_JJJJ_MM\username_JJJJ_MM-xxx-B1-yyy.cfg
            # \home\pc\data3\B_username_JJJJ_MM\username_JJJJ_MM-xxx-B1-yyy.lst
            # where A1= A1...A8 and B1=B1..B8 xxx is local scancounter
            # idea: treat  \home\pc\data as mount_point and _username_JJJJ_MM
            #                                \username_JJJJ_MM-xxx- as prefix
            # srcfiles = '/home/pc/data2/A_' + self.prefix + '-A%d-%03d.lst'

            # strategy: scan mountpoint for files containing prefix in their name
            for dirpath, _, filenames in os.walk(self.sink.fast_basepath):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if self.prefix in filepath:
                        # Gotcha!
                        dstfilename = self.linkpaths[0]+filename
                        # copy file
                        shutil.copyfile(filepath, dstfilename)
                        # XXX: break?

            # link files
            # self.linkpaths enthält den zieldateinamen und die linknamen als eine liste
            # session.data.linkFiles(self.linkpaths[0], self.linkpaths[1:])


class ComtecHeaderSink(ImageSink):
    """Base class for sinks that save arrays to "image" files."""

    attached_devices = {
        'detector': Attach('Fast Detector', ComtecTimer),
    }

    parameters = {
        'fast_basepath': Param('Mount point of the fast data storage',
                               type=str, default='/', settable=False),
    }

    parameter_overrides = {  # \A_username_JJJJ_MM\username_JJJJ_MM-xxx-A1-yyy.lst
        'settypes': Override(default=[POINT, SCAN]),
        'filenametemplate': Override(mandatory=False, settable=False,
                                     userparam=False,
                                     default=['_%(session.experiment.users)s_'
                                              '%(year)04d_%(month)02d/'
                                              '%(session.experiment.users)s_'
                                              '%(year)04d_%(month)02d_'
                                              '%(scancounter)03d_',
                                              '%(proposal)s_%(scancounter)s_'
                                              '%(pointcounter)s_%(pointnumber)s_']),
        'subdir': Override(default='comtec'),
    }

    handlerclass = ComtecHeaderSinkHandler

    def doInit(self, mode):
        if self.mode != SIMULATION:
            # XXX: check existence of 'fast_basepath'
            pass
