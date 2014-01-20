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
from nicos.core import Override, ImageSink
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
Omega=0.000000
omega-2b=%(omega_2b)s
Phi=0.000000
phi-2b=%(phi_2b)s
Chi=0.000000
chi-2b=%(chi_2b)s
BTableX=%(x_2b)s
x-2b=%(x_2b)s
BTableY=%(y_2b)s
y-2b=%(y_2b)s
BTableZ=%(z_2b)s
z-2b=%(z_2b)s
TTableX=%(x_2a)s
x-2a=%(x_2a)s
TTableY=%(y_2a)s
y-2a=%(y_2a)s
TTableZ=%(z_2a)s
z-2a=%(z_2a)s
Temperature=%(T)s
TempDev=%(T)s
Temp1=%(T)s
Temp2=%(Ts)s
Temp3=0.0
Temp4=0.0
Temp5=0.0
Magnet=%(B)s
Pressure=
Thickness=0.0
SlitWidth=
SlitHeight=
SlitDiameter=
Flipper=
Fl1Frequency=302.000000
Fl1Amplitude=0.960000
Fl1Pickup=0.000000
Fl1Temp=0.000000
Fl1Power=0.000000
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
SelSelection=1
Lambda=7.999687
LambdaC=15921
Tilting=-0.003994
Attenuator=0
Polarization=0
PolNeutron=
PolX=0.000000
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

bg1=180.000000
bg2=180.000000
sa1=140.000000
DetSelection=1
det_z-1a=%(det1_z1a)s
SD=%(SD)s
SX=%(det1_x1a)s
SY=0
SR=%(det1_omega1a)s
DetHAngle=0.000000
Beamstop=4
BeamstopX=%(bs1_x1a)s
BeamstopY=%(bs1_y1a)s
DetVoltage=%(hv)s
Moni1Z=0.000000

%%Counter
Sum=%(Sum)s
Time=%(Time)s
Moni1=%(Moni1)s
Moni2=%(Moni2)s
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
%(NICOSHeader)s

%%Counts
"""

class BerSANSFileFormat(ImageSink):
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

        # update info
        imageinfo.data.update(ToDate=strftime('%m/%d/%Y'),
                             ToTime=strftime('%r'),
                             DataSize=shape[0]*shape[1],
                             DataSizeX=shape[1],
                             DataSizeY=shape[0],
                            )
        try:
            SD = '%.1f' % (session.getDevice('det1_z1a').read() -
                           session.getDevice('x_2b').read())
        except Exception as e:
            self.log.warning("can't detemine SD (detector distance), "
                             "using 0 instead: %s"%e)
            SD = 0

        Sum = image.sum()
        if imageinfo.endtime == 0:
            imageinfo.endtime = currenttime()
        Time = imageinfo.endtime - imageinfo.begintime
        Moni1 = 1
        Moni2 = 1
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
                nicosheader.append('%s_%s=%s' %(dev.name, key, value))
        self.log.debug('nicosheader starts with: %40s' % '\n'.join(nicosheader))
        imageinfo.data['NICOSHeader'] = '\n'.join(sorted(nicosheader))

        # write Header
        imageinfo.file.write(BERSANSHEADER % imageinfo.data)

        # write Data (one line per y)
        for y in range(shape[0]):
            line = image[y]
            line.tofile(imageinfo.file, sep=',', format='%d')
            imageinfo.file.write('\n')
        imageinfo.file.flush()

