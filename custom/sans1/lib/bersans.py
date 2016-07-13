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

"""Bersans file format saver, exclusively used at SANS1"""

from time import strftime, localtime, time as currenttime
import numpy as np

from nicos import session
from nicos.core import Override, Param, oneof
from nicos.core.utils import DeviceValueDict
from nicos.devices.datasinks.image import ImageSink, SingleFileSinkHandler
from nicos.pycompat import iteritems, to_ascii_escaped, to_utf8


# not a good solution: BerSANS keys are fixed, but devicenames
# (and their existence) is instrument specific...
#
# Since this used only on SANS1 it will be used like this for the time beeing....
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

%%Sample
SampleName=%(Sample.samplename)s
Environment=%(Environment)s
Position=%(Sample.samplenumber)s
Omega=%(st1_omg)s
omega-2b=%(st1_omg)s
Phi=%(st1_phi)s
phi-2b=%(st1_phi)s
Chi=%(st1_chi)s
chi-2b=%(st1_chi)s
BTableX=%(st1_x)s
x-2b=%(st1_x)s
BTableY=%(st1_y)s
y-2b=%(st1_y)s
BTableZ=%(st1_z)s
z-2b=%(st1_z)s
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
Temp4=0.0
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
Tilting=%(selector_tilt)s
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
col-2a=%(col_2a)s
col-2a_m=%(col_2a_m)s
col-2a_c=%(col_2a_c)s
Col3=0
col-4b=%(col_4b)s
col-4b_m=%(col_4b_m)s
col-4b_c=%(col_4b_c)s
Col4=0
col-4a=%(col_4a)s
col-4a_m=%(col_4a_m)s
col-4a_c=%(col_4a_c)s
Col6=0
col-8b=%(col_8b)s
col-8b_m=%(col_8b_m)s
col-8b_c=%(col_8b_c)s
Col8=0
col-8a=%(col_8a)s
col-8a_m=%(col_8a_m)s
col-8a_c=%(col_8a_c)s
Col10=0
col-12b=%(col_12b)s
col-12b_m=%(col_12b_m)s
col-12b_c=%(col_12b_c)s
Col12=0
col-12a=%(col_12a)s
col-12a_m=%(col_12a_m)s
col-12a_c=%(col_12a_c)s
Col14=0
col-16b=%(col_16b)s
col-16b_m=%(col_16b_m)s
col-16b_c=%(col_16b_c)s
Col16=0
col-16a=%(col_16a)s
col-16a_m=%(col_16a_m)s
col-16a_c=%(col_16a_c)s
Col18=0
col-20b=%(col_20b)s
col-20b_m=%(col_20b_m)s
col-20b_c=%(col_20b_c)s
Col20=0
col-20a=%(col_20a)s
col-20a_m=%(col_20a_m)s
col-20a_c=%(col_20a_c)s

bg1=%(bg1)s
bg2=%(bg2)s
sa1=%(sa1)s
DetSelection=1
det_z-1a=%(det1_z)s
SD=%(SD)s
SX=%(det1_x)s
SY=0
SR=%(det1_omega)s
DetHAngle=0.000000
Beamstop=85x85
BeamstopX=%(bs1_x)s
BeamstopY=%(bs1_y)s
DetVoltage=%(det1_hv_ax)s
Moni1Z=0.000000

%%Counter
Sum=%(Sum)s
Time=%(Time)s
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

%%Comment
MesyDAQFile=%(Histfile)s
ListModeFile=%(Listfile)s
QMesyDAQ_setup_file=%(Setupfile)s
LookUpTable=%(LookUpTable)s
"""

TISANEHEADER = """
tisane_counts=%(tisane_det_pulses)s
tisane_fc=%(tisane_fc)s

tisane_fg1_sample_frequency=%(tisane_fg1.frequency)s
tisane_fg1_sample_amplitude=%(tisane_fg1.amplitude)s
tisane_fg1_sample_offset=%(tisane_fg1.offset)s
tisane_fg1_sample_shape=%(tisane_fg1.shape)s
tisane_fg1_sample_dutycycle=%(tisane_fg1.duty)s

tisane_fg2_sample_frequency=%(tisane_fg2.frequency)s
tisane_fg2_sample_amplitude=%(tisane_fg2.amplitude)s
tisane_fg2_sample_offset=%(tisane_fg2.offset)s
tisane_fg2_sample_shape=%(tisane_fg2.shape)s
tisane_fg2_sample_dutycycle=%(tisane_fg2.duty)s

"""


class BerSANSImageSinkHandler(SingleFileSinkHandler):

    filetype = 'bersans'
    defer_file_creation = True

    def writeHeader(self, fp, metainfo, image):
        shape = image.shape

        try:
            SD = '%.4f' % ((session.getDevice('det1_z').read() -
                           session.getDevice('st1_x').read()) / 1000)
        except Exception:
            self.log.warning("can't determine SD (detector distance), "
                             "using 0 instead", exc=1)
            SD = 0

        finished = currenttime()
        totalTime = finished - self.dataset.started
        Sum = image.sum()
        Moni1 = 0
        Moni2 = 0
        try:
            Moni1 = float(session.getDevice('det1_mon1').read()[0])
            Moni2 = float(session.getDevice('det1_mon2').read()[0])
        except Exception:
            self.log.warning("can't determine all monitors, "
                             "using 0.0 instead", exc=1)

        try:
            det1_image = session.getDevice('det1_image')
            Histfile = det1_image.histogramfile
            Listfile = det1_image.listmodefile.split('\'')[1]
            Setupfile = det1_image.configfile
            LookUpTable = det1_image.calibrationfile
        except Exception:
            Histfile = ''
            Listfile = ''
            Setupfile = 'setup'
            LookUpTable = 'lookup'

        metadata = DeviceValueDict(
            fileName = self._file.filepath,
            fileDate = strftime('%m/%d/%Y', localtime(self.dataset.started)),
            fileTime = strftime('%r', localtime(self.dataset.started)),
            FromDate = strftime('%m/%d/%Y', localtime(self.dataset.started)),
            FromTime = strftime('%r', localtime(self.dataset.started)),
            ToDate = strftime('%m/%d/%Y', localtime(finished)),
            ToTime = strftime('%r', localtime(finished)),
            DataSize = shape[0]*shape[1],
            DataSizeX = shape[1],
            DataSizeY = shape[0],
            Environment = '_'.join(session.explicit_setups),
            SD = SD,
            Sum = '%d' % Sum, Time='%.6f' % totalTime,
            Moni1 = '%d' % Moni1, Moni2='%d' % Moni2,
            Sum_Time = '%.6f' % (Sum / totalTime) if totalTime else 'Inf',
            Sum_Moni1 = '%.6f' % (Sum / Moni1) if Moni1 else 'Inf',
            Sum_Moni2 = '%.6f' % (Sum / Moni2) if Moni2 else 'Inf',
            Histfile = Histfile,
            Listfile = Listfile,
            Setupfile = Setupfile,
            LookUpTable = LookUpTable,
        )

        nicosheader = []

        # no way to map nicos-categories to BerSANS sections :(
        # also ignore some keys :(
        ignore = ('det1_lastlistfile', 'det1_lasthistfile')
        for (dev, param), (value, strvalue, _unit, _category) in \
                iteritems(self.dataset.metainfo):
            devname_key = '%s_%s' % (dev, param)
            if devname_key in ignore:
                continue
            metadata[devname_key] = value
            nicosheader.append('%s=%s' % (devname_key, strvalue))

        nicosheader = b'\n'.join(sorted(map(to_ascii_escaped, nicosheader)))
        self.log.debug('nicosheader starts with: %40s' % nicosheader)

        # write Header
        header = BERSANSHEADER
        if 'tisane' in session.explicit_setups:
            header += TISANEHEADER
        for line in header.split('\n'):
            self.log.debug('testing header line: %r' % line)
            self.log.debug(line % metadata)
            fp.write(to_utf8(line % metadata))
            fp.write(b'\n')

        # also append nicos header
        fp.write(nicosheader.replace(b'\\n', b'\n'))  # why needed?
        fp.write(b'\n\n%Counts\n')
        fp.flush()

    def writeData(self, fp, image):
        # respect flipping options
        if self.sink.flipimage in ['both', 'updown']:
            image = np.flipud(image)
        if self.sink.flipimage in ['both', 'leftright']:
            image = np.fliplr(image)

        # write Data (one line per y)
        for y in range(image.shape[0]):
            line = image[y]
            line.tofile(fp, sep=',', format='%d')
            fp.write(b'\n')
        fp.flush()


class BerSANSImageSink(ImageSink):

    parameters = {
        'flipimage': Param('flip image after reading from det?',
                           type=oneof('none', 'leftright', 'updown', 'both'),
                           default='updown', mandatory=True, unit=''),
    }
    parameter_overrides = {
        'filenametemplate': Override(mandatory=False, settable=False,
                                     userparam=False,
                                     default=['D%(pointcounter)07d.001']),
    }

    handlerclass = BerSANSImageSinkHandler

    def isActiveForArray(self, arraydesc):
        return len(arraydesc.shape) == 2
