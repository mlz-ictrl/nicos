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
#
# *****************************************************************************

"""GALAXI file format saver"""

import numpy

from time import strftime, localtime
from nicos import session
from nicos.core import Override, ImageSink
from nicos.core.utils import DeviceValueDict


class GALAXIFileFormat(ImageSink):
    """Saves GALAXI image data"""

    parameter_overrides = {
        'filenametemplate' : Override(mandatory=False, settable=False,
                                      userparam=False,
                                      default=['%(proposal)s'
                                               '%(Exp.users)s'
                                               '%(session.experiment.sample.'
                                               'samplename)s'
                                               '%(counter)s.g_dat'],
                                     ),
    }

    fileFormat = 'GALAXI'

    def acceptImageType(self, imagetype):
        return True

    def prepareImage(self, imageinfo, subdir=''):
        ImageSink.prepareImage(self, imageinfo, subdir)
        imageinfo.data = DeviceValueDict(fileName=imageinfo.filename,
                                         fileDate=strftime('%m/%d/%Y'),
                                         fileTime=strftime('%r'),
                                         FromDate=strftime('%m/%d/%Y'),
                                         FromTime=strftime('%r'),
                                         Environment='_'.\
                                         join(session.explicit_setups),
                                        )

    def finalizeImage(self, imageinfo):
        """Finalizes the on-disk image, normally just a close"""
        ImageSink.finalizeImage(self, imageinfo)


    def saveImage(self, imageinfo, image):
        """Saves image in GALAXI format"""
        imageinfo.file.seek(0)
        imageinfo.file.write('#\n')
        imageinfo.file.write('# GALAXI Data userid=%s,exp=%s,file=%s,sample=%s\n'
                             % (session.experiment.users,
                                str(session.experiment.lastscan),
                                str(session.experiment.lastimage),
                                session.experiment.sample.samplename))
        imageinfo.file.write('#\n')
        imageinfo.file.write('#' + '-'*79 + '\n')

        imageinfo.file.write('#\n')
        imageinfo.file.write('# User: %s\n' % session.experiment.users)
        imageinfo.file.write('# Sample: %s\n' %
                             session.experiment.sample.samplename)
        imageinfo.file.write('#\n')
        imageinfo.file.write('#' + '-'*79 + '\n')

        self._devreadf = lambda dev: float(session.getDevice(dev).read())
        self._devreadstr = lambda dev: str(session.getDevice(dev).read())
        self._devunit = lambda dev: str(session.getDevice(dev).unit)

        if 'bruker-axs' in session.loaded_setups:
            self._readoutBrukerAXS(imageinfo)
        imageinfo.file.write('#\n')
        imageinfo.file.write('#' + '-'*79 + '\n')
        imageinfo.file.write('#\n')
        imageinfo.file.write('# Motors                         Position\n')
        imageinfo.file.write('#\n')
        if 'collimation' in session.loaded_setups:
            self._readoutCollimation(imageinfo)
        if 'jcns_mot' in session.loaded_setups:
            self._readoutJcnsmot(imageinfo)
        if 'x-ray' in session.loaded_setups:
            self._readoutXray(imageinfo)
        if 'absorber' in session.loaded_setups:
            self._readoutAbsorber(imageinfo)
        if 'pindiodes' in session.loaded_setups:
            self._readoutPindiodes(imageinfo)
        if 'jcns_io' in session.loaded_setups:
            self._readoutJcnsio(imageinfo)
        imageinfo.file.write('#\n')
        imageinfo.file.write('#' + '-'*79 + '\n')
        imageinfo.file.write('#\n')
        begin_t = strftime('%Y-%m-%d %H:%M:%S', localtime(imageinfo.begintime))
        end_t = strftime('%Y-%m-%d %H:%M:%S', localtime(imageinfo.endtime))
        imageinfo.file.write("#    started  at %s\n" % begin_t)
        imageinfo.file.write("#    finished at %s\n" % end_t)
        imageinfo.file.write('#\n')
        imageinfo.file.write('#' + '-'*79 + '\n')

        imageinfo.file.write('#\n')
        imageinfo.file.write('# MYTHEN DATA (number of detectors):  1280\n')
        imageinfo.file.write('#\n')
        values = numpy.array(image)
        for channel in range(1280):
            imageinfo.file.write('#   [%4d] %8d\n' % (channel, values[channel]))

        imageinfo.file.write('#\n')
        imageinfo.file.flush()


    def _readoutBrukerAXS(self, imageinfo):
        """Read bruker devices"""
        imageinfo.file.write('#\n')
        imageinfo.file.write('# Bruker AXS\n')
        imageinfo.file.write('#\n')
        gen_vol = session.getDevice('gen_voltage')
        gen_cur = session.getDevice('gen_current')
        imageinfo.file.write('# X-ray uptime              %9.3f %s\n' \
                         % (self._devreadf('uptime'), self._devunit('uptime')))
        imageinfo.file.write('# X-ray generator    %9.3f %s %9.3f %s\n' \
                             %(float(gen_vol.read()), str(gen_vol.unit),
                               float(gen_cur.read()), str(gen_cur.unit)))
        imageinfo.file.write('# X-ray shutter                 %5s\n' \
                         % self._devreadstr('shutter'))
        imageinfo.file.write('# X-ray tube condition        %7s\n' \
                         % self._devreadstr('tubecond'))
        imageinfo.file.write('# Conditioning interval     %9.3f %s\n' \
                         % (self._devreadf('interval'), self._devunit('interval')))
        imageinfo.file.write('# Conditioning time         %9.3f %s\n' \
                         % (self._devreadf('time'), self._devunit('time')))
        imageinfo.file.write('# X-ray spot position       %9.3f %s\n' \
                         % (self._devreadf('spotpos'), self._devunit('spotpos')))
        imageinfo.file.write('# X-ray stigmator           %9.3f %s\n' \
                         % (self._devreadf('stigmator'), self._devunit('stigmator')))
        imageinfo.file.write('# X-ray vacuum info         %9.3f %s\n' \
                         % (self._devreadf('stigmator'), self._devunit('stigmator')))

    def _readoutCollimation(self, imageinfo):
        """Read collimation devices"""
        imageinfo.file.write('# Slit B1 width             %9.3f %s\n' \
                             % (self._devreadf('b1b'), self._devunit('b1b')))
        imageinfo.file.write('# Slit B1 heigth            %9.3f %s\n' \
                             % (self._devreadf('b1h'), self._devunit('b1h')))
        imageinfo.file.write('# Slit B1 horizontally      %9.3f %s\n' \
                             % (self._devreadf('b1y'), self._devunit('b1y')))
        imageinfo.file.write('# Slit B1 vertically        %9.3f %s\n' \
                             % (self._devreadf('b1z'), self._devunit('b1z')))
        imageinfo.file.write('#\n')
        imageinfo.file.write('# Slit B2 width             %9.3f %s\n' \
                             % (self._devreadf('b2b'), self._devunit('b2b')))
        imageinfo.file.write('# Slit B2 heigth            %9.3f %s\n' \
                             % (self._devreadf('b2h'), self._devunit('b2h')))
        imageinfo.file.write('# Slit B2 horizontally      %9.3f %s\n' \
                             % (self._devreadf('b2y'), self._devunit('b2y')))
        imageinfo.file.write('# Slit B2 vertically        %9.3f %s\n' \
                             % (self._devreadf('b2z'), self._devunit('b2z')))
        imageinfo.file.write('#\n')
        imageinfo.file.write('# Slit B3 width             %9.3f %s\n' \
                             % (self._devreadf('b3b'), self._devunit('b3b')))
        imageinfo.file.write('# Slit B3 heigth            %9.3f %s\n' \
                             % (self._devreadf('b3h'), self._devunit('b3h')))
        imageinfo.file.write('# Slit B3 horizontally      %9.3f %s\n' \
                             % (self._devreadf('b3y'), self._devunit('b3y')))
        imageinfo.file.write('# Slit B3 vertically        %9.3f %s\n' \
                             % (self._devreadf('b3z'), self._devunit('b3z')))

    def _readoutJcnsmot(self, imageinfo):
        """Read some motor devices"""
        imageinfo.file.write('#\n')
        imageinfo.file.write('# BSPY axis                 %9.3f %s\n' \
                             % (self._devreadf('bspy'), self._devunit('bspy')))
        imageinfo.file.write('# BSPZ axis                 %9.3f %s\n' \
                             % (self._devreadf('bspz'), self._devunit('bspz')))
        imageinfo.file.write('#\n')
        imageinfo.file.write('# Detector Z axis           %9.3f %s\n' \
                             % (self._devreadf('detz'), self._devunit('detz')))
        imageinfo.file.write('#\n')
        imageinfo.file.write('# PCHI axis                 %9.3f %s\n' \
                             % (self._devreadf('pchi'), self._devunit('pchi')))
        imageinfo.file.write('# POM axis                  %9.3f %s\n' \
                             % (self._devreadf('pom'), self._devunit('pom')))
        imageinfo.file.write('# PREFZ axis                %9.3f %s\n' \
                             % (self._devreadf('prefz'), self._devunit('prefz')))
        imageinfo.file.write('# PY axis                   %9.3f %s\n' \
                             % (self._devreadf('py'), self._devunit('py')))
        imageinfo.file.write('# PZ axis                   %9.3f %s\n' \
                             % (self._devreadf('pz'), self._devunit('pz')))

    def _readoutXray(self, imageinfo):
        """Read x-ray devices"""
        imageinfo.file.write('#\n')
        imageinfo.file.write('# ROY axis                  %9.3f %s\n' \
                             % (self._devreadf('roy'), self._devunit('roy')))
        imageinfo.file.write('# ROZ axis                  %9.3f %s\n' \
                             % (self._devreadf('roz'), self._devunit('roz')))
        imageinfo.file.write('# ROBY axis                 %9.3f %s\n' \
                             % (self._devreadf('roby'), self._devunit('roby')))
        imageinfo.file.write('# ROBZ axis                 %9.3f %s\n' \
                             % (self._devreadf('robz'), self._devunit('robz')))
        imageinfo.file.write('# DOF chi axis              %9.3f %s\n' \
                             % (self._devreadf('dofchi'), self._devunit('dofchi')))
        imageinfo.file.write('# DOF omega axis            %9.3f %s\n' \
                             % (self._devreadf('dofom'), self._devunit('dofom')))

    def _readoutAbsorber(self, imageinfo):
        """Read absorber devices"""
        imageinfo.file.write('#\n#' + '-'*79 + '\n')
        imageinfo.file.write('#\n')
        imageinfo.file.write('# Absorbers\n')
        imageinfo.file.write('#\n')
        imageinfo.file.write('#   0   01   02   03   04   05   06   07')
        imageinfo.file.write('   08   09   10   11   12   13   14\n')
        imageinfo.file.write('#')
        for i in range(10):
            ab = 'absorber0' + str(i)
            imageinfo.file.write(' %3s ' % self._devreadstr(ab))
        for i in range(10, 15):
            ab = 'absorber' + str(i)
            imageinfo.file.write(' %3s ' % self._devreadstr(ab))
        imageinfo.file.write('\n')

    def _readoutPindiodes(self, imageinfo):
        """Read pindioden devices"""
        imageinfo.file.write('#\n#' + '-'*79 + '\n')
        imageinfo.file.write('#\n')
        imageinfo.file.write('# PIN diodes\n')
        imageinfo.file.write('#\n')
        imageinfo.file.write('# Ionisation chamber 1      %9.3f %s\n' \
                             % (self._devreadf('ionichamber1'),
                                self._devunit('ionichamber1')))
        imageinfo.file.write('#\n')
        imageinfo.file.write('# Ionisation chamber 2      %9.3f %s\n' \
                             % (self._devreadf('ionichamber2'),
                                self._devunit('ionichamber2')))
        imageinfo.file.write('#\n')
        imageinfo.file.write('# PIN diode in chamber 1 position  %3s\n' \
                             % self._devreadstr('pindiode1_move'))
        imageinfo.file.write('# PIN diode in chamber 1    %9.3f %s\n' \
                             % (self._devreadf('pindiode1'), self._devunit('pindiode1')))
        imageinfo.file.write('#\n')
        imageinfo.file.write('# Calibrated PIN diode      %9.3f %s\n' \
                             % (self._devreadf('pindiodecal'),
                                self._devunit('pindiodecal')))
        imageinfo.file.write('#\n')
        imageinfo.file.write('# PIN diode behind sample position %3s\n' \
                             % self._devreadstr('pindiodesample_move'))
        imageinfo.file.write('# PIN diode behind sample   %9.3f %s\n' \
                             % (self._devreadf('pindiodesample'),
                                self._devunit('pindiodesample')))

    def _readoutJcnsio(self, imageinfo):
        imageinfo.file.write('#\n')
        imageinfo.file.write('#' + '-'*79 + '\n')
        imageinfo.file.write('#\n')
        imageinfo.file.write('# GALAXi I/O devices\n')
        imageinfo.file.write('#\n')
        imageinfo.file.write('# Detector distance     %4d %s\n' \
                             % (int(session.getDevice('detdistance').read()),
                               self._devunit('detdistance')))
        imageinfo.file.write('#\n')
        imageinfo.file.write('# Detector tubes\n')
        imageinfo.file.write('#\n')
        imageinfo.file.write('#    01     02     03     04\n')
        imageinfo.file.write('#')
        for i in range(1, 5):
            tube = 'detectube0' + str(i)
            imageinfo.file.write(' %5s ' % self._devreadstr(tube))
        imageinfo.file.write('\n')
        imageinfo.file.write('#\n')
        imageinfo.file.write('# Vacuum tubes\n')
        imageinfo.file.write('#\n')
        imageinfo.file.write('#        01         02         03\n')
        imageinfo.file.write('#')
        for i in range(1, 4):
            tube = 'vacuumtube' + str(i)
            imageinfo.file.write(' %9.3f ' % self._devreadf(tube))
        imageinfo.file.write('    %s\n' % self._devunit(tube))
        imageinfo.file.write('#\n')
        imageinfo.file.write('# Pumps\n')
        imageinfo.file.write('#\n')
        imageinfo.file.write('#    02     03\n')
        imageinfo.file.write('#')
        for i in range(2, 4):
            pump = 'pump0' + str(i)
            imageinfo.file.write(' %5s ' % self._devreadstr(pump))
        imageinfo.file.write('\n')
        imageinfo.file.write('#\n')
        imageinfo.file.write('# Vacuum valves\n')
        imageinfo.file.write('#\n')
        imageinfo.file.write('#    01     02     03     04     05     06\n')
        imageinfo.file.write('#')
        for i in range(1, 7):
            valve = 'vavalve0' + str(i)
            imageinfo.file.write(' %5s ' % self._devreadstr(valve))
        imageinfo.file.write('\n')
        imageinfo.file.write('#\n')
        imageinfo.file.write('# Ventilation valves\n')
        imageinfo.file.write('#\n')
        imageinfo.file.write('#    01     02     03\n')
        imageinfo.file.write('#')
        for i in range(1, 4):
            valve = 'vevalve0' + str(i)
            imageinfo.file.write(' %5s ' % self._devreadstr(valve))
        imageinfo.file.write('\n')


