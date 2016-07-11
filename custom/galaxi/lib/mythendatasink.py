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
#   Lydia Fleischhauer-Fuss <l.fleischhauer-fuss@fz-juelich.de>
#
# *****************************************************************************

"""GALAXI file format saver"""
import numpy

from time import strftime, localtime
from nicos import session
from nicos.core import Override
from nicos.devices.datasinks.image import SingleFileSinkHandler, ImageSink


class MythenImageSinkHandler(SingleFileSinkHandler):

    def writeData(self, fp, data):
        w = fp.write
        w('#\n')
        w('# GALAXI Data userid=%s,exp=%s,file=%s,sample=%s\n'
                             % (session.experiment.users,
                                str(session.experiment.lastscan),
                                str(self.dataset.number),
                                session.experiment.sample.samplename))
        w('#\n')
        w('#' + '-'*79 + '\n')

        w('#\n')
        w('# User: %s\n' % session.experiment.users)
        w('# Sample: %s\n' % session.experiment.sample.samplename)
        w('#\n')
        w('#' + '-'*79 + '\n')

        self._devreadf = lambda dev: float(session.getDevice(dev).read())
        self._devreadstr = lambda dev: str(session.getDevice(dev).read())
        self._devunit = lambda dev: str(session.getDevice(dev).unit)

        if 'bruker-axs' in session.loaded_setups:
            self._readoutBrukerAXS(w)
        w('#\n')
        w('#' + '-'*79 + '\n')
        w('#\n')
        w('# Motors                         Position\n')
        w('#\n')
        if 'collimation' in session.loaded_setups:
            self._readoutCollimation(w)
        if 'jcns_mot' in session.loaded_setups:
            self._readoutJcnsmot(w)
        if 'x-ray' in session.loaded_setups:
            self._readoutXray(w)
        if 'absorber' in session.loaded_setups:
            self._readoutAbsorber(w)
        if 'pindiodes' in session.loaded_setups:
            self._readoutPindiodes(w)
        if 'jcns_io' in session.loaded_setups:
            self._readoutJcnsio(w)
        w('#\n')
        w('#' + '-'*79 + '\n')
        w('#\n')
        begin_t = strftime('%Y-%m-%d %H:%M:%S', localtime(self.dataset.started))
        end_t = strftime('%Y-%m-%d %H:%M:%S', localtime(self.dataset.finished))
        w("#    started  at %s\n" % begin_t)
        w("#    finished at %s\n" % end_t)
        w('#\n')
        w('#' + '-'*79 + '\n')
        w('#\n')
        w('# MYTHEN DATA (number of detectors):  %d   frames:  %d\n'
                          % (data.shape[1],data.shape[0]))
        w('#\n')
        it = numpy.nditer(data, flags=['multi_index'], order='F')
        while it.iterindex+1 < it.itersize  :
            fmtStr = ''.join(['%8d' % it.next() for _ in range(data.shape[0])])
            w('#   [%4d] %s\n' % (it.multi_index[1], fmtStr))
        w('#\n')
        fp.flush()


    def _readoutBrukerAXS(self,w):
        """Read bruker devices"""
        w('#\n')
        w('# Bruker AXS\n')
        w('#\n')
        gen_vol = session.getDevice('gen_voltage')
        gen_cur = session.getDevice('gen_current')
        w('# X-ray uptime              %9.3f %s\n' \
                         % (self._devreadf('uptime'), self._devunit('uptime')))
        w('# X-ray generator    %9.3f %s %9.3f %s\n' \
                             %(float(gen_vol.read()), str(gen_vol.unit),
                               float(gen_cur.read()), str(gen_cur.unit)))
        w('# X-ray shutter                 %5s\n' \
                         % self._devreadstr('shutter'))
        w('# X-ray tube condition        %7s\n' \
                         % self._devreadstr('tubecond'))
        w('# Conditioning interval     %9.3f %s\n' \
                         % (self._devreadf('interval'), self._devunit('interval')))
        w('# Conditioning time         %9.3f %s\n' \
                         % (self._devreadf('time'), self._devunit('time')))
        w('# X-ray spot position       %9.3f %s\n' \
                         % (self._devreadf('spotpos'), self._devunit('spotpos')))
        w('# X-ray stigmator           %9.3f %s\n' \
                         % (self._devreadf('stigmator'), self._devunit('stigmator')))
        w('# X-ray vacuum info         %9.3f %s\n' \
                         % (self._devreadf('stigmator'), self._devunit('stigmator')))

    def _readoutCollimation(self,w):
        """Read collimation devices"""
        w('# Slit B1 width             %9.3f %s\n' \
                             % (self._devreadf('b1b'), self._devunit('b1b')))
        w('# Slit B1 heigth            %9.3f %s\n' \
                             % (self._devreadf('b1h'), self._devunit('b1h')))
        w('# Slit B1 horizontally      %9.3f %s\n' \
                             % (self._devreadf('b1y'), self._devunit('b1y')))
        w('# Slit B1 vertically        %9.3f %s\n' \
                             % (self._devreadf('b1z'), self._devunit('b1z')))
        w('#\n')
        w('# Slit B2 width             %9.3f %s\n' \
                             % (self._devreadf('b2b'), self._devunit('b2b')))
        w('# Slit B2 heigth            %9.3f %s\n' \
                             % (self._devreadf('b2h'), self._devunit('b2h')))
        w('# Slit B2 horizontally      %9.3f %s\n' \
                             % (self._devreadf('b2y'), self._devunit('b2y')))
        w('# Slit B2 vertically        %9.3f %s\n' \
                             % (self._devreadf('b2z'), self._devunit('b2z')))
        w('#\n')
        w('# Slit B3 width             %9.3f %s\n' \
                             % (self._devreadf('b3b'), self._devunit('b3b')))
        w('# Slit B3 heigth            %9.3f %s\n' \
                             % (self._devreadf('b3h'), self._devunit('b3h')))
        w('# Slit B3 horizontally      %9.3f %s\n' \
                             % (self._devreadf('b3y'), self._devunit('b3y')))
        w('# Slit B3 vertically        %9.3f %s\n' \
                             % (self._devreadf('b3z'), self._devunit('b3z')))

    def _readoutJcnsmot(self,w):
        """Read some motor devices"""
        w('#\n')
        w('# BSPY axis                 %9.3f %s\n' \
                             % (self._devreadf('bspy'), self._devunit('bspy')))
        w('# BSPZ axis                 %9.3f %s\n' \
                             % (self._devreadf('bspz'), self._devunit('bspz')))
        w('#\n')
        w('# Detector Z axis           %9.3f %s\n' \
                             % (self._devreadf('detz'), self._devunit('detz')))
        w('#\n')
        w('# PCHI axis                 %9.3f %s\n' \
                             % (self._devreadf('pchi'), self._devunit('pchi')))
        w('# POM axis                  %9.3f %s\n' \
                             % (self._devreadf('pom'), self._devunit('pom')))
        w('# PREFZ axis                %9.3f %s\n' \
                             % (self._devreadf('prefz'), self._devunit('prefz')))
        w('# PY axis                   %9.3f %s\n' \
                             % (self._devreadf('py'), self._devunit('py')))
        w('# PZ axis                   %9.3f %s\n' \
                             % (self._devreadf('pz'), self._devunit('pz')))

    def _readoutXray(self,w):
        """Read x-ray devices"""
        w('#\n')
        w('# ROY axis                  %9.3f %s\n' \
                             % (self._devreadf('roy'), self._devunit('roy')))
        w('# ROZ axis                  %9.3f %s\n' \
                             % (self._devreadf('roz'), self._devunit('roz')))
        w('# ROBY axis                 %9.3f %s\n' \
                             % (self._devreadf('roby'), self._devunit('roby')))
        w('# ROBZ axis                 %9.3f %s\n' \
                             % (self._devreadf('robz'), self._devunit('robz')))
        w('# DOF chi axis              %9.3f %s\n' \
                             % (self._devreadf('dofchi'), self._devunit('dofchi')))
        w('# DOF omega axis            %9.3f %s\n' \
                             % (self._devreadf('dofom'), self._devunit('dofom')))

    def _readoutAbsorber(self,w):
        """Read absorber devices"""
        w('#\n#' + '-'*79 + '\n')
        w('#\n')
        w('# Absorbers\n')
        w('#\n')
        w('#   0   01   02   03   04   05   06   07')
        w('   08   09   10   11   12   13   14\n')
        w('#')
        for i in range(10):
            ab = 'absorber0' + str(i)
            w(' %3s ' % self._devreadstr(ab))
        for i in range(10, 15):
            ab = 'absorber' + str(i)
            w(' %3s ' % self._devreadstr(ab))
        w('\n')

    def _readoutPindiodes(self,w):
        """Read pindioden devices"""
        w('#\n#' + '-'*79 + '\n')
        w('#\n')
        w('# PIN diodes\n')
        w('#\n')
        w('# Ionisation chamber 1      %9.3f %s\n' \
                             % (self._devreadf('ionichamber1'),
                                self._devunit('ionichamber1')))
        w('#\n')
        w('# Ionisation chamber 2      %9.3f %s\n' \
                             % (self._devreadf('ionichamber2'),
                                self._devunit('ionichamber2')))
        w('#\n')
        w('# PIN diode in chamber 1 position  %3s\n' \
                             % self._devreadstr('pindiode1_move'))
        w('# PIN diode in chamber 1    %9.3f %s\n' \
                             % (self._devreadf('pindiode1'), self._devunit('pindiode1')))
        w('#\n')
        w('# Calibrated PIN diode      %9.3f %s\n' \
                             % (self._devreadf('pindiodecal'),
                                self._devunit('pindiodecal')))
        w('#\n')
        w('# PIN diode behind sample position %3s\n' \
                             % self._devreadstr('pindiodesample_move'))
        w('# PIN diode behind sample   %9.3f %s\n' \
                             % (self._devreadf('pindiodesample'),
                                self._devunit('pindiodesample')))

    def _readoutJcnsio(self,w):
        w('#\n')
        w('#' + '-'*79 + '\n')
        w('#\n')
        w('# GALAXi I/O devices\n')
        w('#\n')
        w('# Detector distance     %4d %s\n' \
                             % (int(session.getDevice('detdistance').read()),
                               self._devunit('detdistance')))
        w('#\n')
        w('# Detector tubes\n')
        w('#\n')
        w('#    01     02     03     04\n')
        w('#')
        for i in range(1, 5):
            tube = 'detectube0' + str(i)
            w(' %5s ' % self._devreadstr(tube))
        w('\n')
        w('#\n')
        w('# Vacuum tubes\n')
        w('#\n')
        w('#        01         02         03\n')
        w('#')
        for i in range(1, 4):
            tube = 'vacuumtube' + str(i)
            w(' %9.3f ' % self._devreadf(tube))
        w('    %s\n' % self._devunit(tube))
        w('#\n')
        w('# Pumps\n')
        w('#\n')
        w('#    02     03\n')
        w('#')
        for i in range(2, 4):
            pump = 'pump0' + str(i)
            w(' %5s ' % self._devreadstr(pump))
        w('\n')
        w('#\n')
        w('# Vacuum valves\n')
        w('#\n')
        w('#    01     02     03     04     05     06\n')
        w('#')
        for i in range(1, 7):
            valve = 'vavalve0' + str(i)
            w(' %5s ' % self._devreadstr(valve))
        w('\n')
        w('#\n')
        w('# Ventilation valves\n')
        w('#\n')
        w('#    01     02     03\n')
        w('#')
        for i in range(1, 4):
            valve = 'vevalve0' + str(i)
            w(' %5s ' % self._devreadstr(valve))
        w('\n')


class MythenImageSink(ImageSink):
    """Saves GALAXI image data"""

    parameter_overrides = {
        'filenametemplate':  Override(mandatory=False, settable=False,
                                      userparam=False,
                                      default=['%(Exp.users)s'
                                               '_%(session.experiment.sample.'
                                               'samplename)s_ '
                                               '%(scancounter)s_%(pointnumber)s'
                                               '.mydat']),
    }

    handlerclass = MythenImageSinkHandler
