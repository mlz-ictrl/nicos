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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   Petr Čermák <cermak@mag.mff.cuni.cz>
#
# *****************************************************************************

"""Data sink classes for MGML NICOS."""

from io import TextIOWrapper

from nicos import session
from nicos.core import Override
from nicos.devices.datasinks.scan import AsciiScanfileSink as ass, \
    AsciiScanfileSinkHandler as assh


class AsciiScanfileSinkHandler(assh):

    def prepare(self):
        self.manager.assignCounter(self.dataset)
        addinfo = {'remark': session.experiment.remark}
        fp = self.manager.createDataFile(
            self.dataset, self._template, self.sink.subdir, additionalinfo=addinfo
        )
        self._fname = fp.shortpath
        self._filepath = fp.filepath
        self._file = TextIOWrapper(fp, encoding='utf-8')


class AsciiScanfileSink(ass):
    """A data sink that writes to a plain ASCII data file."""

    handlerclass = AsciiScanfileSinkHandler

    parameter_overrides = {
        'filenametemplate': Override(settable=True),
    }
