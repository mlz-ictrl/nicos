#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Stefanie Keuler <s.keuler@fz-juelich.de>
#   Lydia Fleischhauer-Fuss <l.fleischhauer-fuss@fz-juelich.de>
#
# *****************************************************************************

"""DNS file format saver

.d_dat: document the file format here.
"""

from time import strftime, localtime

import numpy as np

from nicos import session
from nicos.core import Override, ImageSink
from nicos.core.utils import DeviceValueDict


class DNSFileFormat(ImageSink):
    """Saves DNS image data"""
    parameter_overrides = {
        'filenametemplate' : Override(mandatory=False, settable=False,
                                      userparam=False,
                                      default=['%(proposal)s_%(counter)s.d_dat',
                                               '%(proposal)s'
                                               '%(imagecounter)010d'
                                               '%(session.experiment.sample.'
                                               'samplename)s.d_dat'],
                                     ),
    }

    fileFormat = 'DNS'     # should be unique amongst filesavers!

    def acceptImageType(self, imagetype):
        return True

    def prepareImage(self, imageinfo, subdir=''):
        ImageSink.prepareImage(self, imageinfo, subdir)
        imageinfo.data = DeviceValueDict(fileName=imageinfo.filename,
                                         fileDate=strftime('%m/%d/%Y'),
                                         fileTime=strftime('%r'),
                                         FromDate=strftime('%m/%d/%Y'),
                                         FromTime=strftime('%r'),
                                         Environment='_'.join(session.explicit_setups),
                                        )

    def updateImage(self, imageinfo, image):
        """just write the data upon update"""
        imageinfo.file.seek(0)
        numarr = np.array(image)
        imageinfo.file.write("# 64 %4d\n" % 1)
        for ch in range(64):
            imageinfo.file.write("%2d %8d\n" % (ch, numarr[ch]))
        imageinfo.file.flush()

    def finalizeImage(self, imageinfo):
        """finalizes the on-disk image, normally just a close"""
        ImageSink.finalizeImage(self, imageinfo)

    def saveImage(self, imageinfo, image):
        """Save in DNS format"""
        imageinfo.file.seek(0)
        imageinfo.file.write("# DNS Data userid=%s,exp=%s,file=%s,sample=%s\n" %
                (session.experiment.users, str(session.experiment.lastscan),
                 str(session.experiment.lastimage),
                 session.experiment.sample.samplename))
        imageinfo.file.write("#" + "-"*74 + "\n") #separation line
        # TODO: use right value, remove dummylines
        #imageinfo.file.write("# %d\n" % len(datacomment))
        #for i in range(len(datacomment)):
        #    imageinfo.file.write("# " + datacomment[i] + "\n")
        imageinfo.file.write("# 2\n") #Todo: add other comment maybe
        imageinfo.file.write("# User: %s\n" % session.experiment.users)
        imageinfo.file.write("# Sample: %s\n" %
                             session.experiment.sample.samplename)
        imageinfo.file.write("#" + "-"*74 + "\n") #separation line
        imageinfo.file.write("# DNS   Mono  d-spacing[nm]  Theta[deg]   "
                             "Lambda[nm]   Energy[meV]   Speed[m/sec]\n")
        # TODO: not hard coded?
        imageinfo.file.write("#      %s   %6.4f         %6.2f         %6.3f"
                             "%6.3f      %7.2f\n" % ("PG-002", 0.3350,
                            float(session.getDevice('mon_rot').read()), 0.474,
                                                     3.64, 834.6))
        imageinfo.file.write("# Distances [cm] Sample_Chopper    "
                             "Sample_Detector    Sample_Monochromator\n")
        # TODO: not hard coded?
        imageinfo.file.write("#                  36.00            80.00"
                             "            220.00\n")
        imageinfo.file.write("#" + "-"*74 + "\n") #separation line

        imageinfo.file.write("# Motors                      Position\n")
        imageinfo.file.write("# Monochromator              %6.2f deg\n" %
                             float(session.getDevice('mon_rot').read()))
        imageinfo.file.write("# DeteRota                   %6.2f deg\n" %
                             float(session.getDevice('det_rot').read()))
        imageinfo.file.write("#\n")
        imageinfo.file.write("# Huber                      %6.2f deg\n" %
                             float(session.getDevice('sample_rot').read()))
        imageinfo.file.write("# Cradle_lower               %6.2f deg\n" %
                             float(session.getDevice('cradle_lo').read()))
        imageinfo.file.write("# Cradle_upper               %6.2f deg\n" %
                             float(session.getDevice('cradle_up').read()))
        imageinfo.file.write("#\n")
        imageinfo.file.write("# Slit_i_vertical upper      %6.1f mm\n" %
                             float(session.getDevice('ap_sam_y_upper').read()))
        imageinfo.file.write("#                 lower      %6.1f mm\n" %
                             float(session.getDevice('ap_sam_y_lower').read()))
        imageinfo.file.write("# Slit_i_horizontal left     %6.1f mm\n" %
                             float(session.getDevice('ap_sam_x_left').read()))
        imageinfo.file.write("#                   right    %6.1f mm\n" %
                             float(session.getDevice('ap_sam_x_right').read()))
        imageinfo.file.write("#\n")
        #dummy line
        imageinfo.file.write("# Slit_f_upper                %4d mm\n" % 0)
        #dummy line
        imageinfo.file.write("# Slit_f_lower                %4d mm\n" % 0)
        #dummy line
        imageinfo.file.write("# Detector_Position_vertical  %4d mm\n" % 0)
        imageinfo.file.write("#\n")
        imageinfo.file.write("# Polariser\n")
        imageinfo.file.write("#    Translation              %4d mm\n" %
                             int(session.getDevice('pol_trans').read()))
        imageinfo.file.write("#    Rotation              %6.2f deg\n" %
                             float(session.getDevice('pol_rot').read()))
        imageinfo.file.write("#\n")
        imageinfo.file.write("# Analysers                 undefined\n")
        imageinfo.file.write("#" + "-"*74 + "\n") #separation line
        # write currents
        imageinfo.file.write("# B-fields                   current[A]  field[G]\n")
        imageinfo.file.write("#   Flipper_precession        %6.3f A     %6.2f G\n" %
                             (float(session.getDevice('Co').read()), 0.0))
        imageinfo.file.write("#   Flipper_z_compensation    %6.3f A     %6.2f G\n" %
                             (float(session.getDevice('Fi').read()), 0.0))
        imageinfo.file.write("#   C_a                       %6.3f A     %6.2f G\n" %
                             (float(session.getDevice('A').read()), 0.0))
        imageinfo.file.write("#   C_b                       %6.3f A     %6.2f G\n" %
                             (float(session.getDevice('B').read()), 0.0))
        imageinfo.file.write("#   C_c                       %6.3f A     %6.2f G\n" %
                             (float(session.getDevice('C').read()), 0.0))
        imageinfo.file.write("#   C_z                       %6.3f A     %6.2f G\n" %
                             (float(session.getDevice('ZT').read()), 0.0))
        imageinfo.file.write("#" + "-"*74 + "\n") #separation line

        td, tb, tset = float('NaN'), float('NaN'), float('NaN')
        if 'T_jlc3_D' in session.devices:
            td = float(session.getDevice('T_jlc3_D').read())
        if 'T_jlc3_B' in session.devices:
            tb = float(session.getDevice('T_jlc3_B').read())
        if 'T_jlc3_tube' in session.devices:
            tset = float(session.getDevice('T_jlc3_tube').setpoint)

        imageinfo.file.write("# Temperatures/Lakeshore      T\n")
        imageinfo.file.write("#  T1                         %6.3f K\n" % td)
        imageinfo.file.write("#  T2                         %6.3f K\n" % tb)
        imageinfo.file.write("#  sample_setpoint            %6.3f K\n" % tset)
        imageinfo.file.write("#" + "-"*74 + "\n") #separation line

        det_dev = session.getDevice('det')
        imageinfo.file.write("# TOF parameters\n")
        imageinfo.file.write("#  TOF channels                %4d\n" % det_dev.nrtimechan)
        tdiv = 0.05 * (det_dev.divisor + 1)
        imageinfo.file.write("#  Time per channel            %6.1f microsecs\n" % tdiv)
        tdel = 0.05 * det_dev.offsetdelay
        imageinfo.file.write("#  Delay time                  %6.1f microsecs\n" % tdel)

        imageinfo.file.write("#  Chopper slits\n")#        %4d\n" % config.datachopperslits) # todo
        imageinfo.file.write("#  Elastic time channel\n")# %4d\n" % config.dataelastictime) # todo
        imageinfo.file.write("#  Chopper frequency\n")#    %4d Hz\n" % monitor.getfreq()) # todo
        imageinfo.file.write("#" + "-"*74 + "\n") #separation line

        imageinfo.file.write("# Active_Stop_Unit           TIMER\n")
        imageinfo.file.write("#  Timer                    %6.1f sec\n" %
                             float(session.getDevice('timer').read()[0]))
        imageinfo.file.write("#  Monitor           %16d\n" %
                             int(session.getDevice('mon0').read()[0]))
        imageinfo.file.write("#\n")
        begin_t = strftime('%Y-%m-%d %H:%M:%S', localtime(imageinfo.begintime))
        end_t   = strftime('%Y-%m-%d %H:%M:%S', localtime(imageinfo.endtime))
        imageinfo.file.write("#    start   at      %s\n" % begin_t)
        imageinfo.file.write("#    stopped at      %s\n" % end_t)
        imageinfo.file.write("#" + "-"*74 + "\n") #separation line

        # write array
        imageinfo.file.write("# DATA (number of detectors, number of TOF channels)\n")
        numarr = np.array(image)
        imageinfo.file.write("# 64 %4d\n" % det_dev.nrtimechan)
        for ch in range(64):
            imageinfo.file.write("%2d " % ch)
            for q in range(det_dev.nrtimechan):
                imageinfo.file.write(" %8d" % (numarr[q,ch]))
            imageinfo.file.write("\n")
        imageinfo.file.flush()
