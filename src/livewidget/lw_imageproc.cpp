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
// Some of the code has been adapted from code snippets on
//   www.librow.com and www.leptonica.com
//
// *****************************************************************************

#include <iostream>
#include <stdio.h>

#include "lw_common.h"
#include "lw_widget.h"
#include "lw_data.h"
#include "lw_imageproc.h"


//=====================================================================================
//
//  LOW-LEVEL STATIC INLINE FUNCTIONS
//
//=====================================================================================

//---------------------------------------------------------------------------------
//  _medianFilter
//---------------------------------------------------------------------------------

static inline void _medianFilter(float *dest, float *src, int width, int height)
{
    //   Move window through all elements of the image
    for (int y = 1; y < height - 1; ++y)
        for (int x = 1; x < width - 1; ++x) {
            //   Pick up window elements
            int k = 0;
            float window[9];
            for (int j = y - 1; j < y + 2; ++j)
                for (int i = x - 1; i < x + 2; ++i)
                    window[k++] = src[j * width + i];
            //   Order elements (only half of them)
            for (int j = 0; j < 5; ++j) {
                //   Find position of minimum element
                int min = j;
                for (int l = j + 1; l < 9; ++l)
                if (window[l] < window[min])
                    min = l;
                //   Put found minimum element in its place
                const float temp = window[j];
                window[j] = window[min];
                window[min] = temp;
            }
            //   Get result - the middle element
            if (window[4])
                dest[(y - 1) * (width - 2) + x - 1] = window[4];
        }
}


//---------------------------------------------------------------------------------
//  _median
//---------------------------------------------------------------------------------

static inline float _median(float *elements, int N)
{
    //   Order elements (only half of them)
    for (int i = 0; i < (N >> 1) + 1; ++i) {
        //   Find position of minimum element
        int min = i;
        for (int j = i + 1; j < N; ++j)
            if (elements[j] < elements[min])
                min = j;
        //   Put found minimum element in its place
        const float temp = elements[i];
        elements[i] = elements[min];
        elements[min] = temp;
    }
    //   Get result - the middle element
    return elements[N >> 1];
}


//---------------------------------------------------------------------------------
//  _hybridmedianFilter
//---------------------------------------------------------------------------------

static inline void _hybridmedianFilter(float *dest, float *src, int width, int height)
{
    //   Move window through all elements of the image
    for (int m = 1; m < height - 1; ++m)
        for (int n = 1; n < width - 1; ++n) {
            float window[5];
            float results[3];
            //   Pick up cross-window elements
            window[0] = src[(m - 1) * width + n];
            window[1] = src[m * width + n - 1];
            window[2] = src[m * width + n];
            window[3] = src[m * width + n + 1];
            window[4] = src[(m + 1) * width + n];
            //   Get median
            results[0] = _median(window, 5);
            //   Pick up x-window elements
            window[0] = src[(m - 1) * width + n - 1];
            window[1] = src[(m - 1) * width + n + 1];
            window[2] = src[m * width + n];
            window[3] = src[(m + 1) * width + n - 1];
            window[4] = src[(m + 1) * width + n + 1];
            //   Get median
            results[1] = _median(window, 5);
            //   Pick up leading element
            results[2] = src[m * width + n];
            //   Get result
            dest[(m - 1) * (width - 2) + n - 1] = _median(results, 3);
        }
}


//---------------------------------------------------------------------------------
//  _pixelwiseSubtractImages
//---------------------------------------------------------------------------------

static inline void _pixelwiseSubtractImages(float *dest, float *src1, float *src2, int width, int height)
{
    int x, y;

    float *p_src1, *p_src2;
    float *row_src1, *row_src2;
    float *p_dest;

    for (y = 0; y < height; y++) {
        row_src1 = (float *)src1 + y * width;
        row_src2 = (float *)src2 + y * width;
        p_dest = dest + y * width;

        x = 0;
        while (x < width) {
            float value;
            p_src1 = row_src1 + x;
            p_src2 = row_src2 + x;

            value = p_src1[0] - p_src2[0];
            if (value > 0)
                *p_dest = value;
            else
                *p_dest = 0;
            p_dest += 1;
            x += 1;
        }
    }
}


//---------------------------------------------------------------------------------
//  _pixelwiseDivideImages
//---------------------------------------------------------------------------------

static inline void _pixelwiseDivideImages(float *dest, float *src1, float *src2, int width, int height)
{
    int x, y;

    float *p_src1, *p_src2;
    float *row_src1, *row_src2;
    float *p_dest;

    for (y = 0; y < height; y++) {
        row_src1 = (float *)src1 + y * width;
        row_src2 = (float *)src2 + y * width;
        p_dest = dest + y * width;

        x = 0;
        while (x < width) {
            float value;
            p_src1 = row_src1 + x;
            p_src2 = row_src2 + x;

            if (p_src2[0] == 0)
                value = 0;
            else
                value = pow(2, 16) * p_src1[0] / p_src2[0];

            *p_dest = value;
            p_dest += 1;
            x += 1;
        }
    }
}


//---------------------------------------------------------------------------------
//  _despeckleFilter
//---------------------------------------------------------------------------------

static inline void _despeckleFilter(float *dest, float *src, float delta, int width, int height)
{
    int x, y, k;

    float *p11, *p12, *p13;
    float *p21, *p22, *p23; // 3x3 pixel matrix, p22 is the pixel to be despeckled
    float *p31, *p32, *p33;

    float *row1, *row2, *row3;
    float *p_dest;

    k = 0;

    // skip first and last row
    for (y = 1; y < height-1; y++) {
        row1 = (float *)src + (y-1) * width;
        row2 = (float *)src + y * width;
        row3 = (float *)src + (y+1) * width;

        p_dest = dest + y * width;

        x = 0;
        while (x < width) {
            float       d1;
            float       d2;
            float       d3;
            float       d4;
            float       mean_value;

            p11 = row1 - 1 + x;
            p12 = row1     + x;
            p13 = row1 + 1 + x;
            p21 = row2 - 1 + x;
            p22 = row2     + x;
            p23 = row2 + 1 + x;
            p31 = row3 - 1 + x; // XXX p3x are unused!
            p32 = row3     + x;
            p33 = row3 + 1 + x;

            d1 = (float)p22[0] - (float)p21[0];
            d2 = (float)p22[0] - (float)p12[0];
            d3 = (float)p22[0] - (float)p11[0];
            d4 = (float)p22[0] - (float)p13[0];

            if ( (d1 > delta) & (d2 > delta) & (d3 > delta) & (d4 > delta) ) {
            //if ( (d1 > delta) || (d2 > delta) || (d3 > delta) || (d4 > delta) ) {
                mean_value = ( (float)p12[0] + (float)p23[2] + (float)p11[0] + (float)p21[0] ) / 4.;
                k++;
            } else {
                mean_value = (float)p22[0];
            }
            *p_dest = (float) mean_value;
            p_dest += 1;
            x += 1;
        }
    }

    //float percent = round((100.0*k) / (width*height));
    //std::cout << ">> \t" << k << " pixel (about " << percent << "%) have been replaced..." << std::endl;
}



//=====================================================================================
//
//  HIGH-LEVEL FUNCTIONS
//
//=====================================================================================

//---------------------------------------------------------------------------------
//  medianFilter
//
//  -> add copy of first and last line of the image and then call _medianFilter
//---------------------------------------------------------------------------------

void LWImageProc::medianFilter(float *image, int width, int height)
{
    float *extension = new float[(width + 2) * (height + 2)];

    if (!extension)
        return;

    for (int y = 0; y < height; ++y) {
        memcpy(extension + (width + 2) * (y + 1) + 1, image + width * y, width * sizeof(float));
        extension[(width + 2) * (y + 1)] = image[width * y];
        extension[(width + 2) * (y + 2) - 1] = image[width * (y + 1) - 1];
    }

    // add first line
    memcpy(extension, extension + width + 2, (width + 2) * sizeof(float));
    // add last line
    memcpy(extension + (width + 2) * (height + 1), extension + (width + 2) * height, (width + 2) * sizeof(float));

    _medianFilter(image, extension, width + 2, height + 2);

    delete[] extension;
}


//---------------------------------------------------------------------------------
//  hybridmedianFilter
//
//  -> add copy of first and last line of the image and then call _hybridmedianFilter
//---------------------------------------------------------------------------------

void LWImageProc::hybridmedianFilter(float *image, int width, int height)
{
    if (!image || width < 1 || height < 1)
        return;

    float *extension = new float[(width + 2) * (height + 2)];

    if (!extension)
       return;

    for (int i = 0; i < height; ++i) {
        memcpy(extension + (width + 2) * (i + 1) + 1, image + width * i, width * sizeof(float));
        extension[(width + 2) * (i + 1)] = image[width * i];
        extension[(width + 2) * (i + 2) - 1] = image[width * (i + 1) - 1];
    }
    //   Fill first line of image extension
    memcpy(extension,
           extension + width + 2,
           (width + 2) * sizeof(float));
    //   Fill last line of image extension
    memcpy(extension + (width + 2) * (height + 1), extension + (width + 2) * height, (width + 2) * sizeof(float));

    _hybridmedianFilter(image, extension, width + 2, height + 2);

    delete[] extension;
}


//---------------------------------------------------------------------------------
//  pixelwiseAverage
//
//  -> pixelwise average of a list of images identified by their filenames
//---------------------------------------------------------------------------------

void LWImageProc::pixelwiseAverage(float *averageImage, str_vec filenameList, int width, int height)
{
    int x, y;
    int num_images = filenameList.size();

    float *src1 = (float*)malloc(width*height * sizeof(float));
    float *src2 = (float*)malloc(width*height * sizeof(float));

    float *p_src, *p_src1, *p_src2;
    float *row_src, *row_src1, *row_src2;
    float *p_dest;

    if (!averageImage || num_images < 2 || width < 1 || height < 1)
        return;

    std::string str_tmp;

    str_tmp = filenameList.at(0);
    LWData tmpImage( (const char*)str_tmp.data(), TYPE_FITS);
    for(int i = 0; i < width*height; ++i)
        src1[i] = tmpImage.buffer()[i];

    for (int i = 1; i < num_images; i++) {
        str_tmp = filenameList.at(i);
        LWData nextImage((const char*)str_tmp.data(), TYPE_FITS);
        for(int i=0; i<width*height; ++i)
            src2[i] = nextImage.buffer()[i];

        for (y = 0; y < height; y++) {
            row_src1 = src1 + y * width;
            row_src2 = src2 + y * width;
            p_dest = averageImage + y * width;

            x = 0;
            while (x < width) {
                float a_tmp;
                p_src1 = row_src1 + x;
                p_src2 = row_src2 + x;

                a_tmp = (float)p_src1[0] + (float)p_src2[0] ;
                *p_dest = (float) a_tmp;
                p_dest += 1;
                x += 1;
            }
        }
        src1 = averageImage;
    }

    for (y = 0; y < height; y++) {
        row_src = (float *)src1 + y * width;
        p_dest = averageImage + y * width;

        x = 0;
        while (x < width) {
            float d_tmp;
            p_src = row_src + x;

            d_tmp = (float)p_src[0] / (float)num_images;
            *p_dest = (float) d_tmp;
            p_dest += 1;
            x += 1;
        }
    }
}


//---------------------------------------------------------------------------------
//  pixelwiseSubtractImages
//
//  -> pixelwise subtract second image from first image, store result in first image
//---------------------------------------------------------------------------------

void LWImageProc::pixelwiseSubtractImages(float *image_A, float *image_B, int width, int height)
{
    if (!image_A || !image_B || width < 1 || height < 1)
        return;

    _pixelwiseSubtractImages(image_A, image_A, image_B, width, height);
}


//---------------------------------------------------------------------------------
//  pixelwiseDivideImages
//
//  -> pixelwise divide first image by second image, store result in first image
//---------------------------------------------------------------------------------

void LWImageProc::pixelwiseDivideImages(float *image_A, float *image_B, int width, int height)
{
    if (!image_A || !image_B || width < 1 || height < 1)
       return;

    _pixelwiseDivideImages(image_A, image_A, image_B, width, height);
}


//---------------------------------------------------------------------------------
//  despeckleFilter
//
//  -> selective 3x3 despeckle filter
//---------------------------------------------------------------------------------

void LWImageProc::despeckleFilter(float *image, float delta, int width, int height)
{
    if (!image || !delta || width < 1 || height < 1)
        return;

    float *extension = new float[(width + 2) * (height + 2)];

    if (!extension)
        return;

    for (int i = 0; i < height; ++i) {
        memcpy(extension + (width + 2) * (i + 1) + 1, image + width * i, width * sizeof(float));
        extension[(width + 2) * (i + 1)] = image[width * i];
        extension[(width + 2) * (i + 2) - 1] = image[width * (i + 1) - 1];
    }
    //   Fill first line of image extension
    memcpy(extension,
           extension + width + 2,
           (width + 2) * sizeof(float));
    //   Fill last line of image extension
    memcpy(extension + (width + 2) * (height + 1),
           extension + (width + 2) * height,
           (width + 2) * sizeof(float));

    _despeckleFilter(image, image, delta, width, height); // width + 2, height + 2);

    delete[] extension;
}
