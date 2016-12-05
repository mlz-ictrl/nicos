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
#   Lydia Fleischhauer-Fuss <l.fleischhauer-fuss@fz-juelich.de>
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""KWS file format saver"""

from os import path
from time import strftime, localtime

import numpy as np

from nicos import session
from nicos.core import Override
from nicos.core.utils import DeviceValueDict
from nicos.devices.datasinks.image import ImageSink, SingleFileSinkHandler


KWSHEADER = """\
KWS1_MEASUREMENT KFA-IFF spectrum_data file version V-5.00

%(filename)s

Standard_Sample measurement started by Mr(s). kws1 at %(startdate)s

(* Statistics *)
Measurement produced 0 Informations 0 Warnings 0 Errors 0 Fatals

Cyclus_Number Reduce_Data Date_field from to
%(counter)13s          NO               0  0

(* Comment *)
%(Exp.localcontact)s | %(Exp.users)s
%(Exp.remark)s | lambda=%(selector_lambda)sA
%(Sample.samplename)s | %(Sample.comment)s

(* Collimation discription *)
Coll_Position Wind(1)_Pos Beamwindow_X Beamwindow_Y Polarization Lenses
          [m]         [m]         [mm]         [mm]
%(coll_guides)13s %(coll_guides)11s %(coll_x)12s %(coll_y)12s %(polarizer)12s %(lenses)12s
%(coll_guides)13s %(coll_guides)11s %(coll_x)12s %(coll_y)12s %(polarizer)12s %(lenses)12s

(* Detector Discription *)
Li6 Detector is in normal mode. Angle: 0.00 grd
Offset Z_Position X_Position Y_Position
   [m]        [m]       [mm]       [mm]
%(detoffset_m)6s %(det_z)10s %(det_x)10s %(det_y)10s
%(detoffset_m)6s %(det_z)10s %(det_x)10s %(det_y)10s

(* Sample discription *)
Sample_Nr Sample_Pos Thickness Beamwindow_X Beamwindow_Y Time_Factor
                [mm]      [mm]         [mm]         [mm]           *
%(Sample.samplenumber)9s %(sam_trans_x)10s %(Sample.thickness)9s %(ap_sam.width())12s \
%(ap_sam.height())12s %(Sample.timefactor)11s
%(Sample.samplenumber)9s %(sam_trans_y)10s         0 %(ap_sam.centerx())12s \
%(ap_sam.centery())12s

(* Temperature discription *)
%(sample_env_0)s
%(sample_env_1)s
%(sample_env_2)s
%(sample_env_3)s

(* Data_field and Time per Data_Field *)
Data_Field     Time Time_Factor  Repetition
         0 %(exptime)8s %(Sample.timefactor)11s           1

(* Selector and Monitor Counter *)
Selector Monitor_1 Monitor_2 Monitor_3
%(selctr)8s %(mon1)9s %(mon2)9s %(mon3)9s

%(hexapod_0)s
%(hexapod_1)s

(* Calculate measurement time = Time per Data_field*Time_Factor*Repetition *)
%(exptime)8s

(* Real measurement time for detector data *)
%(realtime)12s

"""


class KWSFileSinkHandler(SingleFileSinkHandler):

    filetype = 'KWS'
    accept_final_images_only = True

    def writeData(self, fp, image):
        _collslit = 'aperture_%02d' % session.getDevice('coll_guides').read()
        _exposuretime = session.getDevice('timer').read(0)[0]

        w = fp.write

        # sample envs
        sample_env = ['Temperature dummy line'] * 4
        for (i, (info, val)) in enumerate(zip(self.dataset.envvalueinfo,
                                              self.dataset.envvaluelist)):
            if i >= 4:  # only four lines allowed
                break
            try:
                val = info.fmtstr % val
            except Exception:
                val = str(val)
            sample_env[i] = '%s is Active %s %s' % (info.name, val, info.unit)

        if 'hexapod' in session.loaded_setups:
            hexapod_0 = '(* Hexapod position (tx, ty, tz, rx, ry, rz, dt) *)'
            hexapod_1 = ''
            for axis in ('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'dt'):
                try:
                    hexapod_1 += ' %9.3f' % session.getDevice('hexapod_' + axis).read()
                except Exception:
                    hexapod_1 += ' unknown'
        else:
            hexapod_0 = '(* Measurement stop state *)'
            hexapod_1 = 'measurement STOPPED by USER command'

        # write header
        data = DeviceValueDict()
        data.update(
            startdate = strftime('%d-%b-%Y %H:%M:%S.00',
                                 localtime(self.dataset.started)),
            counter = self.dataset.counter,
            filename = path.basename(fp.filepath),
            coll_x = '%d' % round(session.getDevice(_collslit).width.read()),
            coll_y = '%d' % round(session.getDevice(_collslit).height.read()),
            exptime = '%d min' % (_exposuretime / 60.),
            realtime = '%d sec' % _exposuretime,
            detoffset_m = session.experiment.sample.detoffset / 1000.,
            sample_env_0 = sample_env[0],
            sample_env_1 = sample_env[1],
            sample_env_2 = sample_env[2],
            sample_env_3 = sample_env[3],
            hexapod_0 = hexapod_0,
            hexapod_1 = hexapod_1,
        )
        w(KWSHEADER % data)

        # write "data sum"
        w('(* Detector Data Sum (Sum_Data_Field = 32 values = 6 * 5 and 2) *)\n')
        w('@\n')
        sums = [image.sum()] + [0.0] * 31
        for (i, val) in enumerate(sums):
            w('%E' % val)
            if (i + 1) % 6:
                w(' ')
            else:
                w('\n')
        w('\n\n')

        # write detector data
        if len(image.shape) == 2:
            self._writedet_standard(w, image)
        else:
            self._writedet_tof(w, image, fp)

    def _writedet_standard(self, w, image):
        w('(* Detector Data (Data_Field = 16384 values = 8 * 2048) *)\n')
        w('$\n')

        data = image.ravel()
        for (i, val) in enumerate(data):
            w('%8d ' % val)
            if (i + 1) % 8:
                w(' ')
            else:
                w('\n')

    def _writedet_tof(self, w, image, fp):
        detimg = session.getDevice('det_img')
        cp = session.getDevice('chopper_params')
        chop_params = cp.read()
        if chop_params[0] != 0:  # no chopper in realtime mode
            w('(* Chopper freq=%f Hz, phase=%f deg *)\n' % tuple(chop_params))
            w('\n')
        nslots = image.shape[2]
        w('(* Detector Time Slices: %d slices, unit=us *)\n' % nslots)
        w(' '.join('%8d' % s for s in detimg.slices))
        w('\n\n')

        w('(* Detector Data for %s mode %d timeslots *)\n' %
          (detimg.mode, nslots))
        for i in range(nslots):
            w('(* timeslot %d *)\n' % i)
            np.savetxt(fp, image[:, :, i], fmt='%8d')
            w('\n')


class KWSFileSink(ImageSink):
    """Saves KWS image and header data into a single file"""

    handlerclass = KWSFileSinkHandler

    parameter_overrides = {
        'filenametemplate': Override(mandatory=False, settable=False,
                                     userparam=False,
                                     default=['%(proposal)s_'
                                              '%(pointcounter)d_'
                                              'Stan_'
                                              'C%(coll_guides)s_'
                                              'S%(Sample.samplenumber)s_'
                                              'D0.DAT'],
                                     ),
    }

    def isActiveForArray(self, arraydesc):
        return len(arraydesc.shape) in (2, 3)
