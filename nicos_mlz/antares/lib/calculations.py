#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Tobias Neuwirth <tobias.neuwirth@frm2.tum.de>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

from math import exp, pi

import numpy as np
from scipy import ndimage, signal


def laplace(n, sigma):
    """Laplacian of Gaussian.

    :param N: kernel size.
    :type N: :class:'int'
    :param sigma: width
    :type sigma: :class:'float'
    """
    if np.mod(n, 2) == 0:
        n = n + 1
    n2 = n // 2
    g = np.zeros([n, n])
    log = np.zeros([n, n])
    sigma = float(sigma)
    for i in np.arange(-n2, n2 + 1):
        for j in np.arange(-n2, n2 + 1):
            g[i + n2, j + n2] = exp(
                -(i * i + j * j) / (2. * sigma * sigma))
    sumg = np.sum(g)
    for i in np.arange(-n2, n2 + 1):
        for j in np.arange(-n2, n2 + 1):
            log[i + n2, j + n2] = (i * i + j * j - 2 * sigma * sigma) * \
                g[i + n2, j + n2] / (2. * pi * pow(sigma, 6) * sumg)
    return log


def scharr_filter(img):
    """
    Analysis function for sharpness of an given numpy array.

    First generates a scharr-filter for the x and y direction. Afterwards
    it perfroms a convolution of the scharr with the array and calculates
    the mean value of the absolute.
    Input: region (numpy array)
    Output: sharpness (scalar)
    """
    if img.min() == img.max():
        return 0
    scharr = np.array([[-3 - 3j, 0 - 10j, 3 - 3j],
                       [-10 + 0j, 0 + 0j, 10 + 0j],
                       [-3 + 3j, 0 + 10j, 3 + 3j]])
    grad = signal.convolve2d(img, scharr, boundary='symm', mode='same')
    sharpness = np.mean(np.absolute(grad))
    return sharpness


def gam_rem_adp_log(img, thr3, thr5, thr7, sig_log):
    if img.min() == img.max():
        return img
    # create the kernel of LOG filter
    f_log = -laplace(9, sig_log)
    # do the LOG filter
    img_log = signal.fftconvolve(img, f_log, mode='same')
    # median the LOG edge enhanced image, 3 by 3 is good enough
    img_logm3 = ndimage.median_filter(img_log, (3, 3))

    # substitute only those pixels whose values are greater than adaptive
    # threshold, which is set to median(log(img)) + thr, where thr is a
    # predetermined constant chosed to be best fitted for specific noise
    # charateristics by user.
    # Adaptive filter size:
    # "Opening" operator:
    imgthr3 = np.greater(img_log, img_logm3 + thr3)
    imgthr5 = np.greater(img_log, img_logm3 + thr5)
    imgthr7 = np.greater(img_log, img_logm3 + thr7)

    # we found that some of the edge pixels are not removed. so we dilate
    # the map7
    if np.sum(imgthr7) >= 0:
        s = np.ones([3, 3])  # the dilate structure
        # boxcar smoothing plus threshold to identify single pixel spots
        single7 = signal.convolve2d(imgthr7 * 255, s / np.sum(s),
                                    mode='same') < 30
        # those single pixels in threshold map7
        single7 = single7 & imgthr7
        # take these out of map7 before dilation
        imgthr7 = np.logical_xor(imgthr7, single7)
        # and add them again after dilation
        imgthr7 = np.logical_or(ndimage.binary_dilation(imgthr7, s),
                                single7)

    imgthr5 = np.logical_xor((imgthr5 | imgthr7), imgthr7)
    imgthr3 = np.logical_xor(imgthr3, imgthr5)

    # clean the border of map5 and map7, otherwise there might be out of
    # range error when doing the replacement
    imgthr7[:3, :] = False
    imgthr7[:, :3] = False
    imgthr7[:, -3:] = False
    imgthr7[-3:, :] = False

    imgthr5[:2, :] = False
    imgthr5[:, :2] = False
    imgthr5[:, -2:] = False
    imgthr5[-2:, :] = False

    img_adp = np.copy(img)
    # 3 by 3 median filtering, as substitution image
    imgm3 = ndimage.median_filter(img, (3, 3))

    thr3list = np.nonzero(imgthr3)
    img_adp[thr3list] = imgm3[thr3list]

    index = np.nonzero(imgthr5)
    n5 = np.shape(index)[1]
    for i in range(n5):
        img_adp[index[0][i], index[1][i]] = np.median(
            img[index[0][i] - 2:index[0][i] + 3,
                index[1][i] - 2:index[1][i] + 3])

    index = np.nonzero(imgthr7)
    n7 = np.shape(index)[1]
    for i in range(n7):
        img_adp[index[0][i], index[1][i]] = np.median(
            img[index[0][i] - 3:index[0][i] + 4,
                index[1][i] - 3:index[1][i] + 4])
    return img_adp
