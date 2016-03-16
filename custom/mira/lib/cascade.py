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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Class for CASCADE detector measurement and readout."""

import gzip
from time import sleep, time as currenttime

import numpy

from nicos.devices.tas import Monochromator
from nicos.core import status, tupleof, listof, oneof, Param, Override, \
    Value, CommunicationError, Readable, ImageSink, ImageType, NicosError, \
    HasCommunication
from nicos.devices.generic import ImageChannelMixin, PassiveChannel, \
    ActiveChannel
from nicos.devices.tas.mono import to_k, from_k
from nicos.devices.datasinks.raw import SingleRawImageSinkHandler, \
    SingleRawImageSink
from nicos.core import Attach, SIMULATION

try:
    import nicoscascadeclient as cascadeclient  # pylint: disable=F0401
except ImportError:
    # make the module importable for Jenkins setup-check
    cascadeclient = None


class CascadePadRAWFormat(SingleRAWFileFormat):

    fileFormat = 'CascadePad'

    parameter_overrides = {
        'filenametemplate': Override(default=['%08d.pad'], settable=False),
    }

    def acceptImageType(self, imagetype):
        return len(imagetype.shape) == 2


class CascadeTofRAWFormat(SingleRAWFileFormat):

    fileFormat = 'CascadeTof'

    parameter_overrides = {
        'filenametemplate': Override(default=['%08d.tof'], settable=False),
    }

    def acceptImageType(self, imagetype):
        return len(imagetype.shape) == 3

    def saveImage(self, imageinfo, image):
        gzfp = gzip.GzipFile(mode='wb', fileobj=imageinfo.file)
        gzfp.write(buffer(image))
        self._writeHeader(imageinfo.imagetype, imageinfo.header, gzfp)
        gzfp.close()


class MiraXMLFormat(ImageSink):

    fileFormat = 'MiraXML'

    attached_devices = {
        'timer':     Attach('Timer readout', ActiveChannel),
        'monitor':   Attach('Monitor readout', ActiveChannel),
        'mono':      Attach('Monochromator device to read out', Monochromator),
        'sampledet': Attach('Sample-detector distance readout', Readable),
    }

    parameter_overrides = {
        'filenametemplate': Override(default=['mira_cas_%08d.xml'],
                                     settable=False),
    }

    def doInit(self, mode):
        self._padimg = cascadeclient.PadImage()

    def acceptImageType(self, imagetype):
        # only for 2-D data
        return len(imagetype.shape) == 2

    def updateImage(self, imageinfo, image):
        # no updates written
        pass

    def saveImage(self, imageinfo, image):
        tmp = cascadeclient.TmpImage()
        self._padimg.LoadMem(image.tostring(), 128*128*4)
        tmp.ConvertPAD(self._padimg)
        mon = self._attached_monitor
        timer = self._attached_timer
        mono = self._attached_mono
        tmp.WriteXML(imageinfo.filepath, self._attached_sampledet.read(),
                     from_k(to_k(mono.read(), mono.unit), 'A'),
                     timer.read()[0], mon.read()[0])


class CascadeDetector(HasCommunication, ImageChannelMixin, PassiveChannel):
    """Detector channel for the CASCADE-MIEZE detector.

    Controls the detector via a connection to the CASCADE socket server running
    on a Windows machine.
    """

    # XXX rework timeout mechanism with HasTimeout

    parameters = {
        'server':       Param('"host:port" of the cascade server to connect to',
                              type=str, mandatory=True, preinit=True),
        'debugmsg':     Param('Whether to print debug messages from the client',
                              type=bool, settable=True, default=False),
        'roi':          Param('Region of interest, given as (x1, y1, x2, y2)',
                              type=tupleof(int, int, int, int),
                              default=(-1, -1, -1, -1), settable=True),
        'mode':         Param('Data acquisition mode (tof or image)',
                              type=oneof('tof', 'image'), settable=True),
        'slave':        Param('Slave mode: start together with master device',
                              type=bool, settable=True),
        'preselection': Param('Current preselection (if not in slave mode)',
                              unit='s', settable=True, type=float),
        'lastcounts':   Param('Counts of the last measurement',
                              type=listof(int), settable=True),
        'lastcontrast': Param('Contrast of the last measurement',
                              type=listof(float), settable=True),
        'fitfoil':      Param('Foil for contrast fitting', type=int, default=0,
                              settable=True),
    }

    parameter_overrides = {
        'fmtstr':   Override(default='roi %s, total %s, file %s'),
        'comdelay': Override(default=3.0),
    }

    #
    # helper methods
    #

    # TODO: _checked_communicate currently only used for start
    # (minimum impact, should be used in other places as necessary)
    def _checked_communicate(self, msg, expectedReply=None, errMsg=''):
        for i in range(max(1, self.comtries) - 1, -1, -1):
            try:
                reply = str(self._client.communicate(msg))
                self.log.debug('cascade reply: %r; expected was: %r' %
                               (reply, expectedReply))
                if expectedReply and reply != expectedReply:
                    self._raise_reply(errMsg, reply)
                return reply
            except CommunicationError as e:
                self.log.warning('Communication failed: %s; reset and retry' %
                                 str(e))
                if i:
                    self.reset()
                    sleep(self.comdelay)
                else:
                    raise

    def _raise_reply(self, message, reply):
        """Raise an exception for an invalid reply."""
        if not reply:
            raise CommunicationError(self, message + ': empty reply (reset '
                                     'device to reconnect)')
        raise CommunicationError(self, message + ': ' + str(reply[4:]))

    def _getconfig(self):
        """Return a dictionary with the config from the server."""
        cfg = self._client.communicate('CMD_getconfig_cdr')
        if cfg[:4] != 'MSG_':
            self._raise_reply('could not get configuration', cfg)
        return dict(v.split('=') for v in str(cfg[4:]).split(' '))

    def _getstatus(self):
        """Return a dictionary with the status from the server."""
        st = self._client.communicate('CMD_status_cdr')
        if st == '':
            raise CommunicationError(self, 'no response from server')
        # self.log.debug('got status %r' % st)
        return dict(v.split('=') for v in str(st[4:]).split(' '))

    #
    # parameter handlers
    #

    def doUpdateDebugmsg(self, value):
        if self._mode != SIMULATION:
            cascadeclient.GlobalConfig.SetLogLevel(value and 3 or 0)

    def doReadMode(self):
        return self._getconfig()['mode']

    def doWriteMode(self, value):
        reply = self._client.communicate('CMD_config_cdr mode=%s tres=%d' %
                                         (value, 128 if value == 'tof' else 1)
                                         )
        if reply != 'OKAY':
            self._raise_reply('could not set mode', reply)

    def doUpdateMode(self, value):
        self._dataprefix = (value == 'image') and 'IMAG' or 'DATA'
        self._datashape = (value == 'image') and (128, 128) or (128, 128, 128)
        self._tres = (value == 'image') and 1 or 128

    def doReadPreselection(self):
        return float(self._getconfig()['time'])

    def doWritePreselection(self, value):
        if self.slave:
            self._last_preset = value
            value = 1000000  # master controls preset
        self._last_preset = value
        reply = self._client.communicate('CMD_config_cdr time=%s' % value)
        if reply != 'OKAY':
            self._raise_reply('could not set measurement time', reply)

    #
    # Device/Measurable interface
    #

    def doPreinit(self, mode):
        if cascadeclient is None:
            raise NicosError(self, 'cascadeclient module is not installed, '
                             'cannot use this device class')
        if mode != SIMULATION:
            self._client = cascadeclient.NicosClient()
            self.doReset()

    def doInit(self, mode):
        self._last_preset = self.preselection
        self._started = 0
        self._lastlive = 0
        # self._tres is set by doUpdateMode
        self._xres, self._yres = (128, 128)

    def doShutdown(self):
        self._client.disconnect()

    def doReset(self):
        # restart the cascade server and reconnect
        self._client.communicate('CMD_kill')
        self._client.disconnect()
        host, port = self.server.split(':')
        port = int(port)
        self.log.info('waiting for CASCADE server restart...')
        for _ in range(4):
            sleep(0.5)
            if self._client.connecttohost(host, port):
                break
        else:
            raise CommunicationError(self, 'could not connect to server')
        # reset parameters in case the server forgot them
        self.log.info('re-setting to %s mode' % self.mode.upper())
        self.doWriteMode(self.mode)
        self.doWritePreselection(self.preselection)

    def doStatus(self, maxage=0):
        if not self._client.isconnected():
            return status.ERROR, 'disconnected from server'
        if self._getstatus().get('stop', '0') == '1':
            return status.OK, 'idle'
        else:
            return status.BUSY, 'counting'

    def doStart(self):
        if self.mode == 'image':
            self.readresult = [0, 0]
        else:
            self.readresult = [0, 0, 0., 0., 0., 0.]

        config = cascadeclient.GlobalConfig.GetTofConfig()
        config.SetImageWidth(self._xres)
        config.SetImageHeight(self._yres)
        config.SetImageCount(self._tres)
        config.SetPseudoCompression(False)

        sleep(0.005)
        self._checked_communicate('CMD_start',
                                  'OKAY',
                                  'could not start measurement')
        self._started = currenttime()
        self._lastlivetime = 0

#    def doIsCompleted(self):
#        if currenttime() - self._started > self._last_preset + 10:
#            try:
#                self.doStop()
#            except NicosError:
#                pass
#            raise TimeoutError(self, 'measurement not finished within '
#                               'selected preset time')
#        stopped = self._getstatus().get('stop', '0')
#        if stopped == '1':
#            self._started = 0
#        return stopped
#
    def doStop(self):
        if self.slave:
            self._attached_master.stop()
        else:
            reply = str(self._client.communicate('CMD_stop'))
            if reply != 'OKAY':
                self._raise_reply('could not stop measurement', reply)

    def valueInfo(self):
        cvals = (Value(self.name + '.roi', unit='cts', type='counter',
                       errors='sqrt', active=self.roi != (-1, -1, -1, -1),
                       fmtstr='%d'),
                 Value(self.name + '.total', unit='cts', type='counter',
                       errors='sqrt', fmtstr='%d'))
        if self.mode == 'tof':
            cvals = cvals + (Value(self.name + '.c_roi', unit='',
                                   type='counter', errors='next',
                                   fmtstr='%.4f'),
                             Value(self.name + '.dc_roi', unit='',
                                   type='error', fmtstr='%.4f'),
                             Value(self.name + '.c_tot', unit='',
                                   type='counter', errors='next',
                                   fmtstr='%.4f'),
                             Value(self.name + '.dc_tot', unit='',
                                   type='error', fmtstr='%.4f')
                             )
        return cvals

    #
    # ImageChannelMixin interface
    #

    @property
    def imagetype(self):
        if self.mode == 'image':
            return ImageType('data', self._datashape, '<u4', ['X', 'Y'])
        return ImageType('data', self._datashape, '<u4', ['X', 'Y', 'T'])

    def readFinalImage(self):
        # get current data array from detector
        data = self._client.communicate('CMD_readsram')
        if data[:4] != self._dataprefix:
            self._raise_reply('error receiving data from server', data)
        buf = buffer(data, 4)
        # determine total and roi counts
        total = self._client.counts(data)
        ctotal, dctotal = 0., 0.
        if self.roi != (-1, -1, -1, -1):
            x1, y1, x2, y2 = self.roi
            roi = self._client.counts(data, x1, x2, y1, y2)
            croi, dcroi = 0., 0.
            if self.mode == 'tof':
                fret = self._client.contrast(data, self.fitfoil, x1, x2, y1, y2)
                if fret[0]:
                    croi = fret[1]
                    dcroi = fret[3]
        else:
            roi = total
            croi, dcroi = ctotal, dctotal
        if self.mode == 'tof':
            fret = self._client.contrast(data, self.fitfoil)
            if fret[0]:
                ctotal = fret[1]
                dctotal = fret[3]
            self.readresult = [roi, total, croi, dcroi, ctotal, dctotal]
        else:
            self.readresult = [roi, total]
        # make a numpy array and reshape it correctly
        return numpy.frombuffer(buf, '<u4').reshape(self._datashape)

    def readLiveImage(self):
        now = currenttime()
        if now > (self._lastlivetime + 0.2):
            self._lastlivetime = now
            # get final data including all events from detector
            return self.readFinalImage()
