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

"""Detector image classes for NICOS."""

from os import path
from time import time as currenttime

import numpy

from nicos import session
from nicos.core.device import Device, DeviceMixinBase
from nicos.core.errors import NicosError, ProgrammingError
from nicos.core.params import Param, Attach, subdir, listof


class ImageInfo(object):
    """Class for storing data about image detectors which are passed around.
    """
    # from which detector is this? / which detector to take thae data from?
    detector = None
    # which format does the detector deliver (instance of ImageType)
    imagetype = None
    # wich filesaver is active for this imagetype?
    filesaver = None
    # which (if any) is the currently opened datafile
    file = None
    # shortname of the file
    filename = ''
    # lang name of the file (subpath starting at proposalpath)
    filepath = ''
    # if this is part of a larger dataset, keep a reference to it
    dataset = None
    # also keep a copy of the scanpoint number
    scanpoint = 0
    # header data: mapping categories to lists of (devname, attribute, value) tupels
    header = {}
    # starting timestamp
    begintime = 0
    # final timestamp
    endtime = 0
    # allow filesavers to store additional data here
    data = None

    def __init__(self):
        self.header = {}

    def __repr__(self):
        return repr(self.__dict__)


class ImageType(object):
    """Helper class to represent an image type.

    An image type consists of these attributes:

    * shape, a tuple of lengths in 1 to N dimensions
    * dtype, the data type of a single value, in numpy format
    * dimnames, a list of names for each dimension

    The class can try to determine if a given image-type can be converted
    to another.
    """

    def __init__(self, shape, dtype=None, dimnames=None):
        """creates a datatype with given (numpy) shape and (numpy) data format

        Also stores the 'names' of the used dimensions as a list called dimnames.
        Defaults to 'X', 'Y' for 2D data and 'X', 'Y', 'Z' for 3D data.
        """
        if dtype is None:  # try to derive from a given numpy.array
            dtype = shape.dtype
            shape = shape.shape
        if dimnames is None:
            dimnames = ['X', 'Y', 'Z', 'T', 'E', 'U', 'V', 'W'][:len(shape)]
        self.shape = shape
        self.dtype = dtype
        self.dimnames = dimnames

    def canConvertTo(self, imagetype):
        """checks if we can be converted to the given imagetype"""
        # XXX
        if self.shape != imagetype.shape:
            return False
        if self.dimnames != imagetype.dimnames:
            return False
        return True

    def convertTo(self, data, imagetype):
        """converts given data to given imagetype and returns converted data"""
        if not self.canConvertTo(imagetype):
            raise ProgrammingError('Can not convert to requested datatype')
        return numpy.array(data, dtype=imagetype.dtype)

    def __repr__(self):
        return 'ImageType(%r, %r, %r)' % (self.shape, self.dtype, self.dimnames)


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
        'subdir': Param('Filetype specific subdirectory name for the image files',
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
        s, l, f = exp.createImageFile(self.filenametemplate, subdir, self.subdir,
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

    def updateLiveImage(self, imageinfo, image):
        """Update live image.  The difference between this and `updateImage()`
        is that this method should be called with a greater frequency.

        Useful sinks that implement live displays.
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


class ImageProducer(DeviceMixinBase):
    """
    Mixin for detectors that produce and save images.

    ALL detectors storing images MUST subclass this.
    """

    attached_devices = {
        'fileformats': Attach('Filesavers for all wanted fileformats',
                              ImageSink, multiple=True),
    }

    parameters = {
        'subdir': Param('Detector specific subdirectory name for the image files',
                        type=subdir, mandatory=True, settable=True),
        'lastfilename': Param('Last written file by this detector',
                              type=str, default='', settable=True),
    }

    _imageinfos = []  # stores all active imageinfos
    _header = None
    _saved = False

    need_clear = False
    imagetype = None  # either None or an ImageType instance,
                      # can also be made a property if variable

    def prepareImageFile(self, dataset=None):
        """Should prepare an Image file."""
        self._saved = False
        self.log.debug('prepareImageFile(%r)' % dataset)
        if self.need_clear:
            self.clearImage()
        imageinfos = []
        imagetype = self.imagetype
        for ff in self._adevs['fileformats']:
            if ff.acceptImageType(imagetype):
                imageinfo = ImageInfo()
                imageinfo.detector = self
                imageinfo.imagetype = imagetype
                imageinfo.begintime = currenttime()
                imageinfo.header = self._header if self._header else {}
                imageinfo.filesaver = ff
                imageinfo.scanpoint = dataset.curpoint if dataset else 0
                ff.prepareImage(imageinfo, self.subdir)
                imageinfos.append(imageinfo)
        if dataset:
            for imageinfo in imageinfos:
                imageinfo.dataset = dataset
                imageinfo.header.update(dataset.headerinfo)
            dataset.imageinfos = imageinfos
        self._imageinfos = imageinfos
        for ii in imageinfos:
            if ii.filepath:
                self.lastfilename = path.relpath(imageinfos[0].filepath,
                                                 session.experiment.proposalpath)
                break
        else:
            self.lastfilename = '<none>'

    def addInfo(self, dataset, category, valuelist):
        for imageinfo in self._imageinfos:
            self.log.debug('addInfo(%r, %r)' % (category, valuelist))
            imageinfo.header[category] = valuelist

    def addHeader(self, category, valuelist):
        self.log.debug('addHeader(%r, %r)' % (category, valuelist))
        if self._header:
            self._header[category] = valuelist
        else:
            self._header = {category: valuelist}
        for imageinfo in self._imageinfos:
            imageinfo.header[category] = valuelist

    def updateImage(self, image=Ellipsis):
        """Update the given image.

        If no image is specified, try to fetch one using self.readImage.
        If that returns a valid image, distribute to all ImageInfos.
        """
        if image is Ellipsis:
            image = self.readImage()
        self.log.debug('updateImage(%20r)' % image)
        if image is not None:
            for imageinfo in self._imageinfos:
                imageinfo.filesaver.updateImage(imageinfo, image)

    def updateLiveImage(self, image=Ellipsis):
        """Update live image.  The difference between this and `updateImage()`
        is that this method should be called with a greater frequency.

        If no image is specified, try to fetch one using self.readImage.
        If that returns a valid image, distribute to all ImageInfos.
        """
        if image is Ellipsis:
            image = self.readImage()
        self.log.debug('updateLiveImage(%20r)' % image)
        if image is not None:
            for imageinfo in self._imageinfos:
                imageinfo.filesaver.updateLiveImage(imageinfo, image)

    def saveImage(self, image=Ellipsis):
        """Save the given image content."""
        # trigger saving the image
        # XXX: maybe do this in a thread to avoid delaying the countloop.....
        for imageinfo in self._imageinfos:
            if not imageinfo.endtime:
                imageinfo.endtime = currenttime()
        if not self._saved:
            if image is Ellipsis:
                image = self.readFinalImage()
            self.log.debug('saveImage(%20s)' % ('%r' % image))
            if image is not None:
                for imageinfo in self._imageinfos:
                    if imageinfo.file:
                        imageinfo.filesaver.saveImage(imageinfo, image)
                    # also inform possibly running liveWidgets
                    # tag, filename, dtype, nx, ny, nz, time, data
                    session.updateLiveData(
                        imageinfo.filesaver.fileFormat,
                        imageinfo.filepath,
                        imageinfo.imagetype.dtype,
                        imageinfo.imagetype.shape[0],
                        imageinfo.imagetype.shape[1] if len(imageinfo.imagetype.shape) > 1 else 1,
                        imageinfo.imagetype.shape[2] if len(imageinfo.imagetype.shape) > 2 else 1,
                        imageinfo.endtime-imageinfo.begintime,
                        '')
            else:
                self.log.error("Can't save Image, got no data!")
                return
            # finalize/close image
            for imageinfo in self._imageinfos:
                imageinfo.filesaver.finalizeImage(imageinfo)
                imageinfo.data = None
            # self._imageinfos = []
            self._saved = True
        self._header = None

    def doSave(self, exception=False):
        self.saveImage()

    #
    # HW-specific 'Hooks'
    #

    def clearImage(self):
        """Clear the last Image from the HW and prepare the acquisition of a
        new one.

        This is called before the detector is counting and is intended to be
        used an image-plate like detectors.
        """
        pass

    def readImage(self):
        """Read and returns the current/intermediate image from the HW.

        This is called while the detector is counting.  May return None if not
        supported (as on imageplates).
        """
        return None

    def readFinalImage(self):
        """Read and returns the final image from the HW.

        This is called after the detector finished counting.  It should return
        a numpy array of the right shape and type.
        """
        raise NotImplementedError('implement readFinalImage')
