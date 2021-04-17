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
#   Tobias Neuwirth <tobias.neuwirth@frm2.tum.de>
#
# *****************************************************************************

from math import exp, pi

import cv2
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


def gam_rem_adp_log(img, thr3=25, thr5=100, thr7=400, sig_log=0.8):
    f_log = -laplace(9, sig_log)  # create the kernel of LOG filter

    img_log = cv2.filter2D(
        img, -1, cv2.flip(f_log, -1), borderType=cv2.BORDER_CONSTANT)
    # median the LOG edge enhanced image, 3 by 3 is good enough
    img_logm3 = cv2.medianBlur(img_log, 3)
    # substitute only those pixels whose values are greater than adaptive
    # threshold, which is set to median(log(img))+thr, where thr is a
    # predetermined constant chosed to be best fitted for specific noise
    # charateristics by user.
    # Adaptive filter size:
    # "Opening" operator:
    imgthr3 = np.greater(img_log, img_logm3 + thr3)
    imgthr5 = np.greater(img_log, img_logm3 + thr5)
    imgthr7 = np.greater(img_log, img_logm3 + thr7)

    # we found that some of the edge pixels are not removed. so we dilate the
    # map7
    s = np.ones([3, 3])
    imgthr7 = ndimage.binary_dilation(imgthr7, s)

    # clean the border of map5 and map7, otherwise there might be out of range
    # error when doing the replacement
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
    imgm3 = cv2.medianBlur(img, 3)

    imgm5 = cv2.medianBlur(img, 5)
    # opencv medianBlur only support 8-bit images for kernels > 5
    # https://docs.opencv.org/4.5.2/d4/d86/group__imgproc__filter.html#ga564869aa33e58769b4469101aac458f9
    imgm7 = (256 * cv2.medianBlur((img / 256).astype(np.uint8), 7)).astype(np.int16)

    thr3list = np.nonzero(imgthr3)
    img_adp[thr3list] = imgm3[thr3list]

    thr5list = np.nonzero(imgthr5)
    img_adp[thr5list] = imgm5[thr5list]

    thr7list = np.nonzero(imgthr7)
    img_adp[thr7list] = imgm7[thr7list]

    return img_adp
