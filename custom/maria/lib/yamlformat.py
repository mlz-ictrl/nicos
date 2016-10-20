#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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
#   Stefanie Keuler <s.keuler@fz-juelich.de>
#   Lydia Fleischhauer-Fuss <l.fleischhauer-fuss@fz-juelich.de>
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""MARIA file format saver for the new YAML based format."""

from nicos import session
from nicos.core import Override
from nicos.core.data.dataset import ScanDataset
from nicos.core.device import Readable
from nicos.devices.datasinks.image import ImageSink
from nicos.frm2.yamlbase import YAMLBaseFileSinkHandler


class YAMLFileSinkHandler(YAMLBaseFileSinkHandler):

    filetype = "MLZ.MARIA.2.0-beta1"

    def _write_instr_data(self, meas, image):
        manager = session.data  # get datamanager
        # get corresponding scan dataset with scan info if available
        stack = manager._stack
        if len(stack) >= 2 and isinstance(stack[-2], ScanDataset):
            scands = stack[-2]
            meas["info"] = scands.info
        else:
            meas["info"] = self.dataset.info

        # store device information
        devs = meas["devices"] = []
        # all available nicos devices
        devices = dict(session.devices)
        # log all devices in the dataset
        for (info, val) in zip(self.dataset.devvalueinfo,
                               self.dataset.devvaluelist):
            dev = session.getDevice(info.name)
            state, status = dev.status()
            entry = self._dict()
            entry["name"] = info.name
            entry["unit"] = info.unit
            entry["value"] = val
            entry["state"] = state
            entry["status"] = status
            devs.append(entry)
            # remove devices already logged here
            devices.pop(info.name, None)

        # log all remaining nicos devices
        for name, dev in devices.iteritems():
            if isinstance(dev, Readable):
                entry = self._dict()
                state, status = dev.status()
                entry["name"] = name
                entry["unit"] = self._devpar(name, "unit")
                entry["value"] = self._readdev(name)
                entry["state"] = state
                entry["status"] = status
                devs.append(entry)


class YAMLFileSink(ImageSink):
    """Saves MARIA image data and header in yaml format"""

    parameter_overrides = {
        "filenametemplate": Override(mandatory=False, settable=False,
                                     userparam=False,
                                     default=["%(proposal)s_"
                                              "%(pointcounter)010d.yaml"],
                                     ),
    }

    handlerclass = YAMLFileSinkHandler
