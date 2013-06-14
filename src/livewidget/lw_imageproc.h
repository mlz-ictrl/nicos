// *****************************************************************************
// NICOS-NG, the Networked Instrument Control System of the FRM-II
// Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
//
// This program is free software; you can redistribute it and/or modify it under
// the terms of the GNU General Public License as published by the Free Software
// Foundation; either version 2 of the License, or (at your option) any later
// version.
//
// This program is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
// FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
// details.
//
// You should have received a copy of the GNU General Public License along with
// this program; if not, write to the Free Software Foundation, Inc.,
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
// Module authors:
//   Philipp Schmakat <philipp.schmakat@frm2.tum.de>
//   Georg Brandl <georg.brandl@frm2.tum.de>
//
// *****************************************************************************

#ifndef LW_IMAGEPROC_H
#define LW_IMAGEPROC_H

#include <vector>
#include <string>

#include "lw_common.h"

typedef std::vector<std::string> str_vec;

class LWImageProc
{
  public:
    static void medianFilter(float* image, int width, int height);
    static void hybridmedianFilter(float* image, int width, int height);
    static void despeckleFilter(float* image, float delta, int width, int height);
    static void pixelwiseSubtractImages(float* image_A, float* image_B, int width, int height);
    static void pixelwiseDivideImages(float* image_A, float* image_B, int width, int height);
    static void pixelwiseAverage(float* averageImage, str_vec filenameList, int width, int height);

};

#endif
