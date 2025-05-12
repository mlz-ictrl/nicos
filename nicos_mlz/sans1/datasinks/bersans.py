# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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

"""Bersans file format saver, exclusively used at SANS1"""

import os
import re
from time import localtime, strftime, time as currenttime

import numpy as np

from nicos import session
from nicos.core import Override
from nicos.core.utils import DeviceValueDict
from nicos.devices.datasinks.image import ImageFileReader, ImageSink, \
    SingleFileSinkHandler
from nicos.utils import toAscii

# not a good solution: BerSANS keys are fixed, but devicenames
# (and their existence) is instrument specific...
#
# Since this used only on SANS1 it will be used like this for the time being ...
BERSANSHEADER = """
%%File
FileName=%(fileName)s
FileDate=%(fileDate)s
FileTime=%(fileTime)s
Type=SANSDRaw
Proposal=%(Exp.proposal)s
DataSize=%(DataSize)s
DataSizeX=%(DataSizeX)s
DataSizeY=%(DataSizeY)s
FromDate=%(FromDate)s
FromTime=%(FromTime)s
ToDate=%(ToDate)s
ToTime=%(ToTime)s
Title=%(Exp.title)s
User=%(Exp.users)s
Command=%(Command)s

%%Sample
SampleName=%(Sample.samplename)s
Environment=%(Environment)s
Position=%(SampleChanger)s
Omega=%(st_omg)s
omega-2b=%(st_omg)s
Phi=%(st_phi)s
phi-2b=%(st_phi)s
Chi=%(st_chi)s
chi-2b=%(st_chi)s
BTableX=%(st_x)s
x-2b=%(st_x)s
BTableY=%(st_y)s
y-2b=%(st_y)s
BTableZ=%(st_z)s
z-2b=%(st_z)s
TTableX=%(st2_x)s
x-2a=%(st2_x)s
TTableY=%(st2_y)s
y-2a=%(st2_y)s
TTableZ=%(st2_z)s
z-2a=%(st2_z)s
Temperature=%(T)s
TempDev=%(T)s
Temp1=%(T)s
Temp2=%(Ts)s
Temp3=%(T_ccr19_D)s
Temp4=%(T_ccr19_A)s
Temp5=0.0
Magnet=%(B)s
Pressure=
Thickness=0.0
SlitWidth=
SlitHeight=
SlitDiameter=
Flipper=%(P_spinflipper_forward)s
Fl1Frequency=%(F_spinflipper_hp)s
Fl1Amplitude=%(A_spinflipper_hp)s
Fl1Pickup=%(P_spinflipper_reverse)s
Fl1Temp=%(T_spinflipper)s
Fl1Power=%(P_spinflipper)s
IEEE1=%(ieee_1)s
IEEE2=%(ieee_2)s
IEEE3=%(ieee_3)s
IEEE4=%(ieee_4)s
IEEE5=%(ieee_5)s
IEEE6=%(ieee_6)s
IEEE7=%(ieee_7)s
IEEE8=%(ieee_8)s
IEEE9=%(ieee_9)s
IEEE10=%(ieee_10)s

%%Setup
SelSelection=%(selector_ng)s
Lambda=%(selector_lambda)s
LambdaC=%(selector_rpm)s
Tilting=0.00
Attenuator=%(att)s
Polarization=%(ng_pol)s
Polarization_m=%(ng_pol_m)s
Polarization_c=%(ng_pol_c)s
PolNeutron=
PolX=
PolX_enc=
Collimation=%(col)s
Col1=0
col-2b=%(col_2b)s
col-2b_m=%(col_2b_m)s
col-2b_c=%(col_2b_c)s
Col2=0
col-2=%(col_2)s
col-2_m=%(col_2_m)s
col-2_c=%(col_2_c)s
Col3=0
col-3=%(col_3)s
col-3_m=%(col_3_m)s
col-3_c=%(col_3_c)s
Col4=0
col-4=%(col_4)s
col-4_m=%(col_4_m)s
col-4_c=%(col_4_c)s
Col6=0
col-6=%(col_6)s
col-6_m=%(col_6_m)s
col-6_c=%(col_6_c)s
Col8=0
col-8=%(col_8)s
col-8_m=%(col_8_m)s
col-8_c=%(col_8_c)s
Col10=0
col-10=%(col_10)s
col-10_m=%(col_10_m)s
col-10_c=%(col_10_c)s
Col12=0
col-12=%(col_12)s
col-12_m=%(col_12_m)s
col-12_c=%(col_12_c)s
Col14=0
col-14=%(col_14)s
col-14_m=%(col_14_m)s
col-14_c=%(col_14_c)s
Col16=0
col-16=%(col_16)s
col-16_m=%(col_16_m)s
col-16_c=%(col_16_c)s
Col18=0
col-18=%(col_18)s
col-18_m=%(col_18_m)s
col-18_c=%(col_18_c)s
Col20=0
col-20=%(col_20)s
col-20_m=%(col_20_m)s
col-20_c=%(col_20_c)s

bg1=%(bg1)s
bg2=%(bg2)s
sa1=%(sa1)s
DetSelection=1
det_z-1a=%(det1_z)s
SD=%(SD)s
SX=%(det1_x)s
SY=0
SR=%(det1_omg)s
DetHAngle=0.000000
Beamstop=%(bs1_shape)s
BeamstopX=%(bs1_xax)s
BeamstopY=%(bs1_yax)s
DetVoltage=%(det1_hv_ax)s
Moni1Z=0.000000

%%Counter
Sum=%(Sum)s
Time=%(det1_timer)s
Moni1=%(det1_mon1)s
Moni2=%(det1_mon2)s
Sum/Time=%(Sum_Time)s
Sum/Moni1=%(Sum_Moni1)s
Sum/Moni2=%(Sum_Moni2)s

%%History
Transmission=0.000000
Scaling=0.000000
Probability=0.000000
BeamcenterX=0.000000
BeamcenterY=0.000000
Aperture=0.000000
Activatable=0
TotalSum=
TotalTime=
RadialSteps=
SectorCenter=
SectorWidth=
MaskFile=
Attenuation=
Import=
Merged=
Operation=
ChannelNumber=
ChannelStart=
ChannelWidth=
ChannelCenter=

%%Comment
"""

# TISANEHEADER = """
# tisane_counts=%(tisane_det_pulses)s
# tisane_fc=%(tisane_fc)s
#
# tisane_fg1_sample_frequency=%(tisane_fg1_sample.frequency)s
# tisane_fg1_sample_amplitude=%(tisane_fg1_sample.amplitude)s
# tisane_fg1_sample_offset=%(tisane_fg1_sample.offset)s
# tisane_fg1_sample_shape=%(tisane_fg1_sample.shape)s
# tisane_fg1_sample_dutycycle=%(tisane_fg1_sample.duty)s
#
# tisane_fg2_sample_frequency=%(tisane_fg2_det.frequency)s
# tisane_fg2_sample_amplitude=%(tisane_fg2_det.amplitude)s
# tisane_fg2_sample_offset=%(tisane_fg2_det.offset)s
# tisane_fg2_sample_shape=%(tisane_fg2_det.shape)s
# tisane_fg2_sample_dutycycle=%(tisane_fg2_det.duty)s
#
# """

TISANEHEADER_old = """
tisane_counts=%(tisane_det_pulses)s
tisane_fc=%(tisane_fc)s
tisane_fg_multi=%(tisane_fg_multi.strings)s

"""

TISANEHEADER = """
tisane_counts=%(tisane_det_pulses)s
tisane_fg_multi=%(tisane_fg_multi.strings)s

"""


class BerSANSImageSinkHandler(SingleFileSinkHandler):

    filetype = 'bersans'
    defer_file_creation = True

    def writeHeader(self, fp, metainfo, image):
        shape = image.shape

        try:
            SD = '%.4f' % ((session.getDevice('det1_z').read() -
                           session.getDevice('st_x').read()) / 1000)
        except Exception:
            self.log.warning("can't determine SD (detector distance), "
                             "using 0 instead", exc=1)
            SD = 0

        finished = currenttime()
        # totalTime = finished - self.dataset.started
        Sum = image.sum()
        Moni1 = 0
        Moni2 = 0
        Time = 0
        try:
            Moni1 = float(session.getDevice('det1_mon1').read()[0])
            Moni2 = float(session.getDevice('det1_mon2').read()[0])
            Time = float(session.getDevice('det1_timer').read()[0])
        except Exception:
            self.log.warning("can't determine all monitors, "
                             "using 0.0 instead", exc=1)

        try:
            Histfile = metainfo['det1_image', 'histogramfile'][1]
        except Exception:
            Histfile = ''

        try:
            Listfile = metainfo['det1_image', 'listmodefile'][1].split("'")[1]
        except Exception:
            Listfile = ''

        try:
            Setupfile = metainfo['det1_image', 'configfile'][1]
        except Exception:
            Setupfile = 'setup'

        try:
            LookUpTable = metainfo['det1_image', 'calibrationfile'][1]
        except Exception:
            LookUpTable = 'lookup'

        time_format = '%I:%M:%S %p'
        date_format = '%m/%d/%Y'

        metadata = DeviceValueDict(
            fileName = os.path.basename(self._file.filepath),
            fileDate = strftime(date_format, localtime(self.dataset.started)),
            fileTime = strftime(time_format, localtime(self.dataset.started)),
            FromDate = strftime(date_format, localtime(self.dataset.started)),
            FromTime = strftime(time_format, localtime(self.dataset.started)),
            ToDate = strftime(date_format, localtime(finished)),
            ToTime = strftime(time_format, localtime(finished)),
            DataSize = shape[0]*shape[1],
            DataSizeX = shape[1],
            DataSizeY = shape[0],
            Environment = '_'.join(session.explicit_setups),
            SD = SD,
            Sum = '%d' % Sum,
            Moni1 = '%d' % Moni1,
            Moni2 = '%d' % Moni2,
            Sum_Time = '%.6f' % (Sum / Time) if Time else 'Inf',
            Sum_Moni1 = '%.6f' % (Sum / Moni1) if Moni1 else 'Inf',
            Sum_Moni2 = '%.6f' % (Sum / Moni2) if Moni2 else 'Inf',
            Histfile = Histfile,
            Listfile = Listfile,
            Setupfile = Setupfile,
            LookUpTable = LookUpTable,
            Command = self.dataset.info,
        )

        nicosheader = []

        # no way to map nicos-categories to BerSANS sections :(
        # also ignore some keys :(
        ignore = ('det1_lastlistfile', 'det1_lasthistfile')
        for (dev, param), info in \
                self.dataset.metainfo.items():
            devname_key = '%s_%s' % (dev, param)
            if devname_key in ignore:
                continue
            metadata[devname_key] = info.value
            nicosheader.append('%s=%s' % (devname_key, info.strvalue))

        nicosheader = '\n'.join(sorted(map(toAscii, nicosheader))).encode()
        self.log.debug('nicosheader starts with: %40s', nicosheader)

        # write Header
        header = BERSANSHEADER
        if 'tisane' in session.explicit_setups:
            header += TISANEHEADER
        for line in header.split('\n'):
            self.log.debug('testing header line: %r', line)
            self.log.debug('%s', line % metadata)
            fp.write((line % metadata).encode())
            fp.write(b'\n')

        # also append nicos header
        fp.write(nicosheader.replace(b'\\n', b'\n'))  # why needed?
        fp.write(b'\n\n%Counts\n')
        fp.flush()

    def writeData(self, fp, image):
        # write Data (one line per y)
        for y in range(image.shape[0]):
            line = image[y]
            line.tofile(fp, sep=',', format='%d')
            fp.write(b'\n')
        fp.flush()


class BerSANSImageSink(ImageSink):

    parameter_overrides = {
        'filenametemplate': Override(mandatory=False, settable=False,
                                     userparam=False,
                                     default=['D%(pointcounter)07d.001']),
    }

    handlerclass = BerSANSImageSinkHandler

    def isActiveForArray(self, arraydesc):
        return len(arraydesc.shape) == 2


class BerSANSImageFileReader(ImageFileReader):

    filetypes = [
        ('bersans', 'BerSANS File (*.001)'),
    ]

    @classmethod
    def fromfile(cls, filename):
        cts_found = False
        linenr = 0
        data = np.zeros(shape=(128, 128), dtype='int16')
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('%Counts'):
                    cts_found = True
                    continue
                elif cts_found:
                    data[linenr] = [int(s) for s in re.findall(r'\d+', line)]
                    linenr += 1
        return data
