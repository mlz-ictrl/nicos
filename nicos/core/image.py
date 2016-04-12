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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

"""Detector image classes for NICOS."""

from nicos import session
from nicos.core.device import Device
from nicos.core.errors import NicosError, ProgrammingError
from nicos.core.params import Param, subdir, listof


class ImageSink(Device):
    """
    Abstract baseclass for saving >= 2D image type data.

    Each ImageSink subclass that writes files needs to write either:

    * into a different subdir
    * name files differently to avoid nameclashes

    (both would also be ok.)

    Method calling sequence is as follows:

    - prepareImage (before the dector starts counting, but after it got its
      presets)
    - addHeader (the detector may or may not already count) (called several
      times)
    - updateImage (may be called between 1 and many times, useful for live data
      display and saving the provisional image for long counting times)
    - saveImage (last data transfer, after detector stopped counting)
    - finalizeImage ('clean-up' operation)

    Classes should be able to handle more than one call to saveImage,
    which may happen if a count/scan is interrupted at a specific place.
    """

    parameters = {
        'subdir': Param('Filetype specific subdirectory name for the image '
                        'files',
                        type=subdir, mandatory=False, default=''),
        'filenametemplate': Param('List of templates for data file names '
                                  '(will be hardlinked)', type=listof(str),
                                  default=['%08d.dat'], settable=True),
    }

    # should be unique amongst filesavers!, used for logging/output
    fileFormat = 'undefined'

    def acceptImageType(self, imagetype):
        """Return True if the given imagetype can be saved."""
        raise NotImplementedError('implement acceptImageType')

    def prepareImage(self, imageinfo, subdir=''):
        """Prepare an Imagefile in the given subdir if we support the requested
        imagetype.
        """
        exp = session.experiment
        s, l, f = exp.createImageFile(self.filenametemplate, subdir,
                                      self.subdir,
                                      scanpoint=imageinfo.scanpoint)
        if not f:
            raise NicosError(self, 'Could not create file %r' % l)
        imageinfo.filename = s
        imageinfo.filepath = l
        imageinfo.file = f

    def updateImage(self, imageinfo, image):
        """Update the image with the given content (while measurement is
        still in progress).

        Useful for fileformats wanting to store several states of the
        data-aquisition.
        """
        return None

    def saveImage(self, imageinfo, image):
        """Save the given image content.

        Content MUST be a numpy array with the right shape; if the fileformat
        to be supported has image shaping options, they should be applied here.
        """
        raise NotImplementedError('implement saveImage')

    def finalizeImage(self, imageinfo):
        """Finalize the on-disk image, normally just a close."""
        if imageinfo.file:
            imageinfo.file.close()
            imageinfo.file = None
        else:
            raise ProgrammingError(self, 'finalize before prepare or save '
                                   'called twice!')
