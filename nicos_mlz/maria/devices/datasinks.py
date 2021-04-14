# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2021 by the NICOS contributors (see AUTHORS)
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

from nicos.core import Param, tupleof
from nicos.devices.datasinks.file import TEMPLATE_DESC
from nicos.devices.datasinks.text import NPGZFileSink as BaseNPGZFileSink, \
    NPGZImageSinkHandler as BaseNPGZImageSinkHandler


class NPGZImageSinkHandler(BaseNPGZImageSinkHandler):

    def _createFile(self, **kwargs):
        fp = BaseNPGZImageSinkHandler._createFile(self, **kwargs)
        idx, nametemplates = self.sink.linknametemplate
        _, filepaths = self.manager.getFilenames(self.dataset, nametemplates,
                                                 self.sink.subdir,
                                                 **kwargs)
        # create hardlinks for the idx' file configured in linknametemplate
        self.manager.linkFiles(self._files[idx].filepath, filepaths)
        return fp


class NPGZFileSink(BaseNPGZFileSink):
    handlerclass = NPGZImageSinkHandler

    parameters = {
        'linknametemplate': Param('Template for the data file name hardlinked'
                                  'to the i-th file configured using'
                                  '(i, [nametemplates]).',
                                  type=tupleof(int, list),
                                  mandatory=True,settable = False,
                                  prefercache = False, ext_desc=TEMPLATE_DESC),
    }
