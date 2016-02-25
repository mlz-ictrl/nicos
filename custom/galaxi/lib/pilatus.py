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
#   Alexander Steffens <a.steffens@fz-juelich.de>
#   Lydia Fleischhauer-Fuß <l.fleischhauer-fuss@fz-juelich.de>
#
# *****************************************************************************

"""GALAXI Pilatus detector"""


from nicos import session
from nicos.core import waitForStatus, status, usermethod, MASTER
from nicos.core.device import Readable, Measurable
from nicos.core.params import Param, dictof, subdir, Attach
from nicos.devices.tango import PyTangoDevice
from nicos.devices.datasinks import AsciiDatafileSink

P_TIME = 't'
P_FRAMES = 'f'


class PilatusDetector(PyTangoDevice, Measurable):
    """Basic Tango device for Pilatus detector."""

    STRSHAPE = ['x', 'y', 'z', 't']
    MXMAPPING = {'detdistance':'Detector_distance',
                 'det2th':'Detector_2theta',
                 'detz':'Detector_Voffset',
                 'ionichamber2':'Flux',
                 'absorber': 'Filter_transmission',
                 'pchi':'Chi',
                 'pom':'Omega'
    }

    attached_devices = {
        'detdistance': Attach('Pilatus detector distance', Readable),
#    '    det2th': Attach('Pilatus detector distance', Readable), -> Einbau!
        'detz': Attach('Pilatus detector 2theta axis', Readable),
        'ionichamber2': Attach('Ionisation chamber 2', Readable),
        'absorber': Attach('Absorber attenuation', Readable),
        'pchi': Attach('Sample Chi axis', Readable),
        'pom': Attach('Sample Omega axis', Readable)
    }

    parameters = {
        'detshape':     Param('Shape of Pilatus detector',
                              type=dictof(str, int)),
        'energyrange':  Param('X-ray energy range', type=list,
                              default=[9224.7, 9251.7]),
        'wavelength':   Param('X-ray wavelength', type =float, default=1.341),
        'energy':       Param('X-ray energy', type=float, unit='keV',
                              settable=True, volatile=True),
        'threshold':    Param('Energy threshold', type=float, unit='keV',
                              settable=True, volatile=True),
        'expperframe':  Param('Number of exposures accumulated to one frame',
                              type=int, settable=True, volatile=True),
        'frames':       Param('Number of images within an acquisition',
                              type=int, settable=True, volatile=True),
        'time':         Param('Exposure time of one image', type=int, unit='s',
                              settable=True, volatile=True),
        'period':       Param('Time between two frames of an exposure',
                              type=float, unit='s', settable=True,
                              volatile=True),
        'remaining':    Param('Remaining exposure time', type=int, unit='s',
                              volatile=True),
        'kbblocks':     Param('Number of available 1 KB blocks on the image \
                              path', type=int, unit='KB', volatile=True),
        'nextfilename': Param('Name of next image file', type=str,
                              settable=True),
        'lastimage':    Param('Name of last created image file', type=str,
                              volatile=True),
        'pathorigin':   Param('Origin image path of cam server', type=str),
        'imagepath':    Param('Name of directory where image files will be \
                              saved at', type=str, volatile=True),
        'headerstring': Param('String to be included in the image header',
                              type=str, settable=True, volatile=True),
        'subdir':       Param('Subdir for the tif files', type=subdir,
                              default='', mandatory=False, settable=True),
        'mxsettings':   Param('Crystallographic parameters reported in the \
                              image header', type=dictof(str, str),
                              volatile=True),
    }

    def doInit(self, mode):
        self.log.debug('Pilatus detector init')
        for ds in session.datasinks:
            if isinstance(ds, AsciiDatafileSink):
                self._asciiFile = ds
        self._f = self.frames
        self._t = self.time
        if self._mode == MASTER:
            self.doWriteMxsettings()
            self._pollParam('mxsettings')

    def presetInfo(self):
        return (P_TIME, P_FRAMES)

    def doSetPreset(self, **preset):
        self.log.debug('Pilatus detector set preset')
        if P_TIME in preset:
            self.doWriteTime(preset[P_TIME])
        if P_FRAMES in preset:
            self.doWriteFrames(preset[P_FRAMES])

    def doRead(self, maxage=0):
        """Returns remaining exposure time while an acquisition is running

        Returns last image filename after end of an acquisition"""
        self.log.debug('Pilatus detector read')
        lastImage = self.lastimage
        splitted = lastImage.split('/')
        return self.subdir + splitted[len(splitted)-1]

    def doReadDetshape(self):
        shapeValues = self._dev.detectorSize
        detShape = dict()
        for i in range(4):
            detShape[self.STRSHAPE[i]] = shapeValues[i]
        return detShape

    def doReadEnergy(self):
        return self._dev.energy

    def doWriteEnergy(self, value):
        self._dev.energy = value

    def doReadThreshold(self):
        return self._dev.threshold

    def doWriteThreshold(self, value):
        self._dev.threshold = value

    def doReadExpperframe(self):
        return self._dev.expPerFrame

    def doWriteExpperframe(self, value):
        self._dev.expPerFrame = value

    def doReadFrames(self):
        return self._dev.frames

    def doWriteFrames(self, value):
        self._dev.frames = value

    def doReadTime(self):
        return self._dev.syncValue

    def doWriteTime(self, value):
        self._dev.syncValue = value

    def doReadPeriod(self):
        return self._dev.period

    def doWritePeriod(self, value):
        self._dev.period = value

    def doReadRemaining(self):
        return self._dev.remainingTime

    def doReadKbblocks(self):
        return self._dev.kbBlocks

    def doReadNextfilename(self):
        return self._dev.nextFilename

    def doWriteNextfilename(self, value):
        self._dev.nextFilename = value

    def doWriteSubdir(self, value):
        if value != '':
            self._asciiFile._setROParam('subdir', value)
            value = value + '/'
        self._dev.imagePath = self.pathorigin + value
        self._pollParam('imagepath')
        return value

    def doReadLastimage(self):
        return self._dev.lastFilename

    def doReadImagepath(self):
        return self._dev.imagePath

    def doReadHeaderstring(self):
        return self._dev.headerString

    def doWriteHeaderstring(self, value):
        self._dev.headerString = value

    def doReadMxsettings(self):
        mxValues = {}
        rawValues = self._dev.mxSettings
        rawValues = rawValues.replace('#', '').replace('\r', '').strip()
        if rawValues != 'none set':
            valueList = rawValues.split('\n')
            for entry in valueList:
                mxValuePair = entry.strip().split(' ', 1)
                mxValues[mxValuePair[0]] = mxValuePair[1]
        return mxValues

    def doWriteMxsettings(self):
        mxValues = 'Wavelength ' + str(self.wavelength)
        mxValues += (' ' + self.MXMAPPING['det2th'] +  ' 0')
        for adev in self._adevs:
            mxValues += (' ' + self.MXMAPPING[adev] + ' ')
            if adev == 'absorber':
                mxValues += str(1/self._adevs[adev].read())
            elif adev == 'detdistance':
                mxValues += str(self._adevs[adev].read()*0.001)
            else:
                mxValues += str(self._adevs[adev].read())
        mxValues += ' Energy_range ' + str(self.energyrange[0]) + ' '\
                                     + str(self.energyrange[1])
        self._dev.mxSettings = mxValues

    def doPrepare(self):
        self.log.debug('Pilatus detector prepare')
        self._scanpoint = self._asciiFile.lastpoint + 1
        exp = session.experiment
        fname = exp.users + '_' + exp.sample.samplename + '_'\
                + str(exp.lastscan) + '_' + str(self._scanpoint) + '.tif'
        self._dev.nextFilename = fname
        self._pollParam('nextfilename')
        self.doWriteMxsettings()
        self._dev.Prepare()

    def doStart(self):
        self.log.debug('Pilatus detector wait for status')
        waitForStatus(self, ignore_errors=True)
        self.log.debug('Pilatus detector start')
        self._dev.Start()

    def doStatus(self, maxage=0):
        if PyTangoDevice.doStatus(self, 0)[0] == status.BUSY:
            info ='Remaining exposure time:    ' + str(self.remaining) + ' s'
            return (status.BUSY, info)
        else:
            return PyTangoDevice.doStatus(self, 0)

    def doStop(self):
        self.log.debug('Pilatus detector stop')
        self._dev.Stop()

    def doFinish(self):
        pass

    def doReset(self):
        self.log.debug('Pilatus detector reset')
        self._dev.Reset()
        self._t = self.time
        self._f = self.frames

    @usermethod
    def sendCommand(self, command):
        """Send any command to Pilatus"""
        return self._dev.SendCommand(command)

    @usermethod
    def thRead(self, channel):
        """Read temperature and humidity sensors"""
        return self._dev.THread(channel)
