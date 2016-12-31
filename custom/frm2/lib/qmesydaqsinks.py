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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""QMesyDAQ file writer classes."""

from nicos import session
from nicos.core import Attach, DataSinkHandler, Override
from nicos.devices.datasinks.image import ImageSink
from nicos.devices.vendor.qmesydaq import Image


class HistogramSinkHandler(DataSinkHandler):

    def prepare(self):
        session.data.assignCounter(self.dataset)
        filepaths = session.data.getFilenames(self.dataset,
                                              self.sink.filenametemplate,
                                              self.sink.subdir)[1]
        self.sink._attached_image.histogramfile = filepaths[0]


class ListmodeSinkHandler(DataSinkHandler):

    def prepare(self):
        session.data.assignCounter(self.dataset)
        filepaths = session.data.getFilenames(self.dataset,
                                              self.sink.filenametemplate,
                                              self.sink.subdir)[1]
        self.sink._attached_image.listmodefile = filepaths[0]


class QMesyDAQSink(ImageSink):
    """Base class for the QMesyDAQ related data files.

    The class reimplements all methods to avoid real data writing in NICOS
    itself. It ensures that the listmode and/or histogram data files will be
    written via QMesyDAQ itself. It uses the settings of the NICOS to define
    the names of the files but the directory to write the data is set in
    QMesyDAQ.
    """
    attached_devices = {
        'image': Attach('Image device to set the file name', Image,
                        optional=True),
    }

    def isActiveForArray(self, arraydesc):
        return len(arraydesc.shape) == 2


class HistogramSink(QMesyDAQSink):
    """Writer for the histogram files via QMesyDAQ itself."""

    handlerclass = HistogramSinkHandler

    parameter_overrides = {
        'filenametemplate': Override(mandatory=False, userparam=False,
                                     default=['D%(pointcounter)07d.mtxt']),
    }


class ListmodeSink(QMesyDAQSink):
    """Writer for the list mode files via QMesyDAQ itself."""

    handlerclass = ListmodeSinkHandler

    parameter_overrides = {
        'filenametemplate': Override(mandatory=False, userparam=False,
                                     default=['D%(pointcounter)07d.mdat']),
    }
