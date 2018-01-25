#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

"""File data sink classes for PUMA."""

from nicos.core import INFO_CATEGORIES, Override, Param
from nicos.core.errors import ConfigurationError
from nicos.devices.datasinks.image import ImageSink, SingleFileSinkHandler

from nicos.pycompat import TextIOWrapper, iteritems


class PolarizationFileSinkHandler(SingleFileSinkHandler):
    """."""

    defer_file_creation = True

    def writeHeader(self, fp, metainfo, image):
        fp.seek(0)
        wrapper = TextIOWrapper(fp)
        wrapper.write('\n%s PUMA Polarisation File Header V2.0\n' %
                      (self.sink.commentchar * 3))
        # XXX(dataapi): add a utility function to convert metainfo to old
        # by-category format
        bycategory = {}
        for (device, key), (_, val, unit, category) in iteritems(metainfo):
            if category:
                bycategory.setdefault(category, []).append(
                    ('%s_%s' % (device, key), (val + ' ' + unit).strip()))
        for category, catname in INFO_CATEGORIES:
            if category not in bycategory:
                continue
            wrapper.write('%s %s\n' % (self.sink.commentchar * 3, catname))
            for key, value in sorted(bycategory[category]):
                wrapper.write('%25s : %s\n' % (key, value))
        # to ease interpreting the data...
        # wrapper.write('\n%r' % self._arraydesc)
        wrapper.write('\n')
        wrapper.detach()
        fp.flush()

    def writeData(self, fp, image):
        """Write the image data part of the file (second part)."""
        wrapper = TextIOWrapper(fp)
        for i, l in enumerate(image.T):
            fmtstr = '\t'.join(['%d'] * (1 + len(l))) + '\n'
            wrapper.write(fmtstr % ((i,) + tuple(l.tolist())))
        wrapper.detach()
        fp.flush()


class PolarizationFileSink(ImageSink):
    """A data sink that writes to a plain ASCII data file."""

    parameters = {
        'commentchar': Param('Comment character', type=str, default='#',
                             settable=True),
    }

    parameter_overrides = {
        'filenametemplate': Override(default=['puma_%(pointcounter)08d']),
    }

    handlerclass = PolarizationFileSinkHandler

    def doUpdateCommentchar(self, value):
        if len(value) > 1:
            raise ConfigurationError('comment character should only be one '
                                     'character')
