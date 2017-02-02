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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Class for CASCADE detector measurement and readout (via Windows server)."""

from time import sleep, time as currenttime

import numpy as np

from nicos.core import Param, Override, Value, Attach, ArrayDesc, Readable, \
    SIMULATION, tupleof, oneof, status, CommunicationError, NicosError
from nicos.core.data import GzipFile
from nicos.core.mixins import HasCommunication
from nicos.devices.datasinks.raw import SingleRawImageSink
from nicos.devices.datasinks.image import ImageSink, SingleFileSinkHandler
from nicos.devices.generic.detector import ActiveChannel
from nicos.devices.tas.mono import Monochromator, to_k, from_k
from nicos.devices.generic.detector import PassiveChannel, ImageChannelMixin

try:
    import nicoscascadeclient as cascadeclient  # pylint: disable=F0401
except ImportError:
    # make the module importable for Jenkins setup-check
    cascadeclient = None


class CascadeDetector(HasCommunication, ImageChannelMixin, PassiveChannel):
    """Detector channel for the CASCADE-MIEZE detector."""

    parameters = {
        'server':   Param('Host:port of server', type=str, mandatory=True),
        'roi':      Param('Region of interest, given as (x1, y1, x2, y2)',
                          type=tupleof(int, int, int, int),
                          default=(-1, -1, -1, -1), settable=True),
        'mode':     Param('Data acquisition mode (tof or image)',
                          type=oneof('tof', 'image'), settable=True),
        'fitfoil':  Param('Foil for contrast fitting', type=int, default=0,
                          settable=True),
        'preselection': Param('Current preselection (if not in slave mode)',
                              unit='s', settable=True, type=float),
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
                self.log.debug('cascade reply: %r; expected was: %r',
                               reply, expectedReply)
                if expectedReply and reply != expectedReply:
                    self._raise_reply(errMsg, reply)
                return reply
            except CommunicationError as e:
                self.log.warning('Communication failed: %s; reset and retry',
                                 e)
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
        # self.log.debug('got status %r', st)
        return dict(v.split('=') for v in str(st[4:]).split(' '))

    #
    # parameter handlers
    #

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
        self._last_preset = value
        value = 1000000  # master controls preset
        reply = self._client.communicate('CMD_config_cdr time=%s' % value)
        if reply != 'OKAY':
            self._raise_reply('could not set measurement time', reply)

    #
    # Device interface
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
        # self._tres is set by doUpdateMode
        self._xres, self._yres = (128, 128)

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
        self.log.info('re-setting to %s mode', self.mode.upper())
        self.doWriteMode(self.mode)
        self.doWritePreselection(self.preselection)

    def doStatus(self, maxage=0):
        if not self._client.isconnected():
            return status.ERROR, 'disconnected from server'
        if self._getstatus().get('stop', '0') == '1':
            return status.OK, 'idle'
        else:
            return status.BUSY, 'counting'

    #
    # Channel interface
    #

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

    def doFinish(self):
        # stopped by the master, but wait for detector to actually
        # finish countloop
        while self._getstatus().get('stop', '0') != '1':
            sleep(0.005)

    def doStop(self):
        # wait for detector to actually finish countloop
        while self._getstatus().get('stop', '0') != '1':
            sleep(0.005)

    def valueInfo(self):
        cvals = (Value(self.name + '.roi', unit='cts', type='counter',
                       errors='sqrt', fmtstr='%d'),
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
                                   type='error', fmtstr='%.4f'))
        return cvals

    @property
    def arraydesc(self):
        if self.mode == 'image':
            return ArrayDesc('data', self._datashape, '<u4', ['X', 'Y'])
        return ArrayDesc('data', self._datashape, '<u4', ['X', 'Y', 'T'])

    def doReadArray(self, quality):
        # get current data array from detector
        rawdata = self._client.communicate('CMD_readsram')
        if rawdata[:4] != self._dataprefix:
            self._raise_reply('error receiving data from server', rawdata)
        buf = buffer(rawdata, 4)
        data = np.frombuffer(buf, '<u4').reshape(self._datashape)
        # determine total and roi counts
        total = data.sum()
        ctotal, dctotal = 0., 0.
        # XXX implement for MIEZE
        # if self.mode == 'tof':
        #     ctotal =
        #     dctotal =
        if self.roi != (-1, -1, -1, -1):
            x1, y1, x2, y2 = self.roi
            roi = data[x1:x2, y1:y2].sum()
            croi, dcroi = 0., 0.
            # XXX implement for MIEZE
            # if self.mode == 'tof':
            #     croi =
            #     dcroi =
        else:
            roi = total
            croi, dcroi = ctotal, dctotal
        if self.mode == 'tof':
            self.readresult = [roi, total, croi, dcroi, ctotal, dctotal]
        else:
            self.readresult = [roi, total]
        # make a numpy array and reshape it correctly
        return data


class CascadePadSink(SingleRawImageSink):

    parameter_overrides = {
        'filenametemplate': Override(default=['%(pointcounter)08d.pad'],
                                     settable=False),
    }

    def isActiveForArray(self, arraydesc):
        return len(arraydesc.shape) == 2


class CascadeTofSink(SingleRawImageSink):

    parameter_overrides = {
        'filenametemplate': Override(default=['%(pointcounter)08d.tof'],
                                     settable=False),
    }

    fileclass = GzipFile

    def isActiveForArray(self, arraydesc):
        return len(arraydesc.shape) == 3


class MiraXmlHandler(SingleFileSinkHandler):
    filetype = 'xml'
    accept_final_images_only = True

    def writeData(self, fp, image):
        mon = self.sink._attached_monitor
        timer = self.sink._attached_timer
        mono = self.sink._attached_mono
        write = fp.write
        write('''\
<measurement_file>

<instrument_name>MIRA</instrument_name>
<location>Forschungsreaktor Muenchen II - FRM2</location>

<measurement_data>
<Sample_Detector>%d</Sample_Detector>
<wavelength>%.2f</wavelength>
<lifetime>%.3f</lifetime>
<beam_monitor>%d</beam_monitor>
<resolution>1024</resolution>

<detector_value>\n''' % (self.sink._attached_sampledet.read(),
                         from_k(to_k(mono.read(), mono.unit), 'A'),
                         timer.read()[0],
                         mon.read()[0]))

        w, h = image.shape
        if self.sink._format is None or self.sink._format[0] != image.shape:
            p = []
            for _x in range(w):
                for fx in range(1024 // w):
                    for _y in range(h):
                        for fy in range(1024 // h):
                            if fx % 4 == 0 and fy % 4 == 0:
                                p.append('%f ')
                            else:
                                p.append('0 ')
                    p.append('\n')
            self.sink._format = (image.shape, ''.join(p))

        filled = np.repeat(np.repeat(image, 256 // w, 0), 256 // h, 1)
        write(self.sink._format[1] % tuple(filled.ravel() / 4.))

        write('''\
</detector_value>

</measurement_data>

</measurement_file>
''')


class MiraXmlSink(ImageSink):

    handlerclass = MiraXmlHandler

    attached_devices = {
        'timer':     Attach('Timer readout', ActiveChannel),
        'monitor':   Attach('Monitor readout', ActiveChannel),
        'mono':      Attach('Monochromator device to read out', Monochromator),
        'sampledet': Attach('Sample-detector distance readout', Readable),
    }

    parameter_overrides = {
        'filenametemplate': Override(default=['mira_cas_%(pointcounter)08d.xml'],
                                     settable=False),
    }

    _format = None

    def isActiveForArray(self, arraydesc):
        # only for 2-D data
        return len(arraydesc.shape) == 2
