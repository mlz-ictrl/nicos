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
//   Georg Brandl <georg.brandl@frm2.tum.de>
//
// *****************************************************************************

#ifndef LW_COMMON_H
#define LW_COMMON_H

enum LWFiletype {
    TYPE_NONE               = 0,
    TYPE_CASCADE            = 1,
    TYPE_FITS               = 2,
    TYPE_TOFTOF             = 3
};

enum LWCtrl {
    Logscale                = 0x0001,
    Grayscale               = 0x0002,
    Cyclic                  = 0x0004,
    CreateProfile           = 0x0008,
    Histogram               = 0x0010,
    MinimumMaximum          = 0x0020,
    BrightnessContrast      = 0x0040,
    Integrate               = 0x0080,
    ImageOperations         = 0x0100,
    Despeckle               = 0x0200,
    Normalize               = 0x0400,
    Darkfield               = 0x0800,
    ShowGrid                = 0x1000,
    Filelist                = 0x2000
};

enum LWImageFilters {
    NoImageFilter           = 0,
    MedianFilter            = 1,
    HybridMedianFilter      = 2,
    DespeckleFilter         = 3
};

enum LWImageOperations {
    NoImageOperation        = 0,
    OpenBeamNormalization   = 1,
    DarkImageSubtraction    = 2,
    StackAverage            = 3,
    ImageMultiplyByFloat    = 4,
    PixelwiseAddition       = 5,
    PixelwiseSubtraction    = 6,
    PixelwiseDivision       = 7,
    PixelwiseMultiplication = 8,
    StackMedian             = 9,
    StackMinimum            = 10,
    StackMaximum            = 11
};

#endif
