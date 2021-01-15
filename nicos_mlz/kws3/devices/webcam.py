#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

import requests

from nicos.core import Override, Param
from nicos.core.constants import POINT
from nicos.core.data import DataSink
from nicos.devices.datasinks.file import FileSink
from nicos.devices.datasinks.image import SingleFileSinkHandler


class WebcamSinkHandler(SingleFileSinkHandler):
    filetype = 'jpg'

    def _processArrayInfo(self, _):
        pass

    def _createFile(self, **kwargs):
        kwargs['nomeasdata'] = True
        return SingleFileSinkHandler._createFile(self, **kwargs)

    def begin(self):
        try:
            resp = requests.get(self.sink.url, timeout=1)
            resp.raise_for_status()
            self._file.write(resp.content)
        except Exception as e:
            self.log.warning('could not get webcam image: %s', e)

    def putResults(self, quality, result):
        pass

    def putMetainfo(self, metainfo):
        pass


class WebcamSink(FileSink):
    """Copies a snapshot of a webcam to the data directory."""

    parameters = {
        'url': Param('URL of the image', type=str, mandatory=True),
    }

    parameter_overrides = {
        'settypes': Override(default=[POINT])
    }

    handlerclass = WebcamSinkHandler

    def isActive(self, dataset):
        return DataSink.isActive(self, dataset)
