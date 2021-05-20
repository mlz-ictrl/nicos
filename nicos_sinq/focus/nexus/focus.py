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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************
"""This file contains special elements for writing FOCUS NeXus files"""

import numpy as np

from nicos import session
from nicos.core import FINAL, INTERMEDIATE, INTERRUPTED
from nicos.core.errors import ConfigurationError
from nicos.nexus.elements import CalcData, NamedImageDataset, NexusElementBase


class SliceTofImage(CalcData):
    """
    This selects a subset of an image whose last
    dimension is a tof array. This code does not work in
    a general way but only for the detectorID-TOF 2D array
    of FOCUS
    """
    def __init__(self, image_name, tof_name, start_slice, end_slice, **attrs):
        self._start_slice = start_slice
        self._end_slice = end_slice
        self._image_name = image_name
        self._tof_name = tof_name
        self.dtype = 'int32'
        self._detectorIDX = -1
        self._imageIDX = -1
        CalcData.__init__(self, **attrs)

    def _shape(self, dataset):
        tof = session.getDevice(self._tof_name)
        n = self._end_slice - self._start_slice
        if n > 1:
            return self._end_slice - self._start_slice, tof.dim[0]-1
        else:
            return tof.dim[0]-1,

    def locateImage(self, dataset):
        detID = 0
        imageID = 0
        for det in dataset.detectors:
            arList = det.arrayInfo()
            for ar in arList:
                if ar.name == self._image_name:
                    self._detectorIDX = detID
                    self._imageIDX = imageID
                    break
                imageID += 1
            detID += 1
        if detID == -1 or imageID == -1:
            self.log.warning('Cannot find named image %s', self._image_name)

    def _calcData(self, dataset):
        if self._imageIDX == -1:
            self.locateImage(dataset)
        if self._imageIDX == -1:
            return None
        det = dataset.detectors[self._detectorIDX]
        # Be persistent in getting at array data
        arrayData = det.readArrays(FINAL)
        if arrayData is None:
            arrayData = det.readArrays(INTERRUPTED)
            if arrayData is None:
                arrayData = det.readArrays(INTERMEDIATE)
        if arrayData is not None:
            data = arrayData[self._imageIDX]
            return data[self._start_slice:self._end_slice]


class SumImage(CalcData):
    """
    Sum all the TOF channels together for FOCUS
    """
    def __init__(self, image_name, dim,  **attrs):
        self._image_name = image_name
        self.dtype = 'int32'
        self._detectorIDX = -1
        self._imageIDX = -1
        self._dim = dim
        CalcData.__init__(self, **attrs)

    def _shape(self, dataset):
        return [self._dim, ]

    def locateImage(self, dataset):
        detID = 0
        imageID = 0
        for det in dataset.detectors:
            arList = det.arrayInfo()
            for ar in arList:
                if ar.name == self._image_name:
                    self._detectorIDX = detID
                    self._imageIDX = imageID
                    break
                imageID += 1
            detID += 1
        if detID == -1 or imageID == -1:
            self.log.warning('Cannot find named image %s', self._image_name)

    def _calcData(self, dataset):
        if self._imageIDX == -1:
            self.locateImage(dataset)
        if self._imageIDX == -1:
            return None
        det = dataset.detectors[self._detectorIDX]
        # Be persistent in getting at array data
        arrayData = det.readArrays(FINAL)
        if arrayData is None:
            arrayData = det.readArrays(INTERRUPTED)
            if arrayData is None:
                arrayData = det.readArrays(INTERMEDIATE)
        if arrayData is not None:
            data = arrayData[self._imageIDX]
            if data is not None:
                return data.sum(axis=1)


class FocusCoordinates(NexusElementBase):
    """
    This class stores the FOCUS coordinate arrays living
    in device f2d_coords in the NeXus file.
    """
    def create(self, name, h5parent, sinkhandler):
        try:
            coord = session.getDevice('f2d_coords')
        except ConfigurationError:
            session.log.warning('2D coords not found, cannot write '
                                '2D detector meta data')
            return
        xdim = coord.xdim
        ydim = coord.ydim
        shape = (xdim, ydim)
        dset = h5parent.create_dataset('x_value', shape, maxshape=shape,
                                       chunks=shape,
                                       dtype='float32',
                                       compression='gzip')
        data = np.array(coord.xval)
        dset[...] = data.reshape(shape)
        dset = h5parent.create_dataset('y_value', shape, maxshape=shape,
                                       chunks=shape,
                                       dtype='float32',
                                       compression='gzip')
        data = np.array(coord.yval)
        dset[...] = data.reshape(shape)
        dset = h5parent.create_dataset('distance', shape, maxshape=shape,
                                       chunks=shape,
                                       dtype='float32',
                                       compression='gzip')
        data = np.array(coord.distval)
        dset[...] = data.reshape(shape)
        dset = h5parent.create_dataset('equatorial_angle', shape,
                                       maxshape=shape,
                                       chunks=shape,
                                       dtype='float32',
                                       compression='gzip')
        data = np.array(coord.eqval)
        dset[...] = data.reshape(shape)
        dset = h5parent.create_dataset('azimuthal_angle', shape,
                                       maxshape=shape,
                                       chunks=shape,
                                       dtype='float32',
                                       compression='gzip')
        data = np.array(coord.azval)
        dset[...] = data.reshape(shape)
        dset = h5parent.create_dataset('polar_angle', shape, maxshape=shape,
                                       chunks=shape,
                                       dtype='float32',
                                       compression='gzip')
        data = np.array(coord.tthval)
        dset[...] = data.reshape(shape)


class ScaledImage(NamedImageDataset):
    """
    For some reason, the data from the 2D HM is multiplied by 100.
    This class corrects this
    """
    def update(self, name, h5parent, sinkhandler, values):
        if not self.valid:
            return
        det = sinkhandler.dataset.detectors[self.detectorIDX]
        # Be persistent in getting at array data
        arrayData = det.readArrays(FINAL)
        if arrayData is None:
            arrayData = det.readArrays(INTERRUPTED)
        if arrayData is None:
            arrayData = det.readArrays(INTERMEDIATE)
        if arrayData is not None:
            data = arrayData[self.imageIDX]
            if data is not None:
                dset = h5parent[name]
                if self.doAppend:
                    if len(dset) < self.np + 1:
                        self.resize_dataset(dset, sinkhandler)
                    dset[self.np] = data/100
                else:
                    h5parent[name][...] = data/100
