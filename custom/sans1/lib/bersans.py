#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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

from time import strftime, time as currenttime
import numpy as np

from nicos import session
from nicos.core import Override, ImageSink, Param, oneof
from nicos.core.utils import DeviceValueDict

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
Position=%(Sample.activesample)s
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
Flipper=%(P_spinflipper.forward)s
Fl1Frequency=%(F_spinflipper_hp)s
Fl1Amplitude=%(A_spinflipper_hp)s
Fl1Pickup=%(P_spinflipper.reverse)s
Fl1Temp=%(T_spinflipper)s
Fl1Power=%(P_spinflipper)s
IEEE1=
IEEE2=
IEEE3=
IEEE4=
IEEE5=
IEEE6=
IEEE7=
IEEE8=
IEEE9=
IEEE10=

%%Setup
SelSelection=%(selector_ng)s
Lambda=%(selector_lambda)s
LambdaC=%(selector_rpm)s
Tilting=%(selector_tilt)s
Attenuator=%(att)s
Polarization=%(ng_pol)s
PolNeutron=
PolX=
PolX_enc=
Collimation=%(col)s
Col1=0
col-2b=%(col_2b)s
Col2=0
col-2a=%(col_2a)s
Col3=0
col-4b=%(col_4b)s
Col4=0
col-4a=%(col_4a)s
Col6=0
col-8b=%(col_8b)s
Col8=0
col-8a=%(col_8a)s
Col10=0
col-12b=%(col_12b)s
Col12=0
col-12a=%(col_12a)s
Col14=0
col-16b=%(col_16b)s
Col16=0
col-16a=%(col_16a)s
Col18=0
col-20b=%(col_20b)s
Col20=0
col-20a=%(col_20a)s

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
DetVoltage=%(hv)s
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

"""

class BerSANSFileFormat(ImageSink):
    parameters = {
        'flipimage' : Param('flip image after reading from det?',
                            type=oneof('none','leftright','updown','both'),
                            default='updown', mandatory=True, unit=''),
    }
    parameter_overrides = {
        'filenametemplate' : Override(mandatory=False, settable=False,
                                      userparam=False,
                                      default=['D%(counter)07d.001']),
    }

    fileFormat = 'BerSANS'     # should be unique amongst filesavers!

    def acceptImageType(self, imagetype):
        return len(imagetype.shape) == 2

    def prepareImage(self, imageinfo, subdir=''):
        """should prepare an Imagefile in the given subdir"""
        ImageSink.prepareImage(self, imageinfo, subdir)
        imageinfo.data = DeviceValueDict(fileName=imageinfo.filename,
                                 fileDate=strftime('%m/%d/%Y'),
                                 fileTime=strftime('%r'),
                                 FromDate=strftime('%m/%d/%Y'),
                                 FromTime=strftime('%r'),
                                 Environment='_'.join(session.explicit_setups),
                                 #~ scantype=dataset.scantype, #XXX
                                 #~ MovingDevices=dataset.devices,
                                 #~ Envlist=dataset.envlist,
                                 #~ Preset=dataset.preset,
                                 #~ scaninfo=dataset.sinkinfo,
                                )

    def saveImage(self, imageinfo,  image):
        """Saves the given image content

        content MUST be a numpy array with the right shape
        if the fileformat to be supported has image shaping options,
        they should be applied here.
        """
        # stupid validator, making sure we have a numpy.array:
        image = np.array(image)
        shape = image.shape

        # savety check
        if len(shape) != 2:
            self.log.error('can not save data with shape %r, '
                           'can only handle 2D-data!' % shape)
            return

        # respect flipping options
        # XXX: check if this should go elsewhere!
        # or each Filesaver needs this as well (-> stupid)
        if self.flipimage in ['both', 'updown']:
            image = np.flipud(image)
        if self.flipimage in ['both', 'leftright']:
            image = np.fliplr(image)

        # update info
        imageinfo.data.update(ToDate=strftime('%m/%d/%Y'),
                             ToTime=strftime('%r'),
                             DataSize=shape[0]*shape[1],
                             DataSizeX=shape[1],
                             DataSizeY=shape[0],
                            )
        try:
            SD = '%.4f' % ((session.getDevice('det1_z').read() -
                           session.getDevice('st1_x').read())
                           /1000)
        except Exception:
            self.log.warning("can't determine SD (detector distance), "
                             "using 0 instead", exc=1)
            SD = 0

        if imageinfo.endtime == 0:
            imageinfo.endtime = currenttime()
        Time = imageinfo.endtime - imageinfo.begintime
        Sum = image.sum()
        Moni1 = 0
        Moni2 = 0
        try:
            Moni1 = float(session.getDevice('det1_mon1').read()[0])
            Moni2 = float(session.getDevice('det1_mon2').read()[0])
        except Exception:
            self.log.warning("can't determine all monitors, "
                             "using 0.0 instead", exc=1)

        imageinfo.data.update(
                             SD=SD,
                             Sum='%d' % Sum, Time='%.6f' % Time,
                             Moni1='%d' % Moni1, Moni2='%d' % Moni2,
                             Sum_Time='%.6f' % (Sum / Time) if Time else 'Inf',
                             Sum_Moni1='%.6f' %(Sum / Moni1) if Moni1 else 'Inf',
                             Sum_Moni2='%.6f' %(Sum / Moni2) if Moni2 else 'Inf',
                            )
        nicosheader = []
        self.log.debug('imageInfo.header is %r' % imageinfo.header)
        # no way to map nicos-categories to BerSANS sections
        for _, valuelist in imageinfo.header.items():
            for dev, key, value in valuelist:
                imageinfo.data['%s_%s' % (dev.name, key)] = value
                nicosheader.append('%s_%s=%r' % (dev.name, key, value))
        nicosheader = '\n'.join(sorted(l.decode('ascii', 'ignore').encode('unicode_escape') for l in nicosheader))
        self.log.debug('nicosheader starts with: %40s' % nicosheader)

        # write Header
        for line in BERSANSHEADER.split('\n'):
            self.log.debug('testing header line: %r' % line)
            self.log.debug(line % imageinfo.data)
            imageinfo.file.write(line % imageinfo.data)
            imageinfo.file.write('\n')

        # also append nicos header
        imageinfo.file.write(nicosheader.replace('\\n','\n')) #? why needed?
        imageinfo.file.write("\n\n%Counts\n")

        # write Data (one line per y)
        for y in range(shape[0]):
            line = image[y]
            line.tofile(imageinfo.file, sep=',', format='%d')
            imageinfo.file.write('\n')
        imageinfo.file.flush()
