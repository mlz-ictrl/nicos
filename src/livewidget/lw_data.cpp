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
//   Tobias Weber <tobias.weber@frm2.tum.de>
//   Georg Brandl <georg.brandl@frm2.tum.de>
//   Philipp Schmakat <philipp.schmakat@frm2.tum.de>
//
// *****************************************************************************

#include <assert.h>
#include <iostream>
#include <limits>
#include <math.h>
#include <time.h>

#include <fitsio.h>

#include "lw_data.h"
#include "lw_imageproc.h"
#include "lw_common.h"

#ifdef CLOCKING
static clock_t clock_start, clock_stop;
#define CLOCK_START()      clock_start = clock()
#define CLOCK_STOP(action) clock_stop  = clock(); \
                           std::cout << (action) << ": " << \
                               (1000 * (float)(clock_stop-clock_start)/CLOCKS_PER_SEC) \
                               << "ms" << std::endl
#else
#define CLOCK_START()
#define CLOCK_STOP(action)
#endif


static inline double safe_log10(double v)
{
    v = (v > 0.) ? log10(v) : -1;
    if (v != v) v = -1.;
    return v;
}

static inline uint16_t bswap_16(uint16_t x)
{
    return (x << 8) | (x >> 8);
}

static inline uint32_t bswap_32(uint32_t x) {
    return (bswap_16(x & 0xFFFF) << 16) | bswap_16(x >> 16);
}

static inline float bswap_32_float(float x)
{
    float res;
    char *d = (char *)&res, *s = (char *)&x;
    *d++ = s[3]; *d++ = s[2]; *d++ = s[1]; *d++ = s[0];
    return res;
}

static inline float bswap_64_float(double x)
{
    double res;
    char *d = (char *)&res, *s = (char *)&x;
    *d++ = s[7]; *d++ = s[6]; *d++ = s[5]; *d++ = s[4];
    *d++ = s[3]; *d++ = s[2]; *d++ = s[1]; *d++ = s[0];
    return res;
}


/** LWData ********************************************************************/

void LWData::_dummyInit()
{
    m_width = m_height = m_depth = 1;
    // simple constructor: create a 1-element array
    m_data = new data_t[1];
    m_clone = new data_t[1];
    m_data[0] = m_clone[0] = 0;
    m_data_owned = true;
    updateRange();
}

LWData::LWData()
    : m_width(1),
      m_height(1),
      m_depth(1),
      m_log10(0),
      m_custom_range(0)
{
    _dummyInit();
}


void LWData::initFromBuffer(const char *data)
{
    m_data = new data_t[size()];
    m_clone = new data_t[size()];

    m_data_owned = true;
    if (m_data == NULL || m_clone == NULL) {
        std::cerr << "could not allocate memory for data" << std::endl;
        return;
    }
    if (data) {
        memcpy(m_data, data, sizeof(data_t) * size());
        memcpy(m_clone, data, sizeof(data_t) * size());
        updateRange();
    } else {
        memset(m_data, 0, sizeof(data_t) * size());
        memset(m_clone, 0, sizeof(data_t) * size());
        m_min = m_max = 0;
    }
}


LWData::LWData(int width, int height, int depth, const char *data)
    : m_width(width),
      m_height(height),
      m_depth(depth),
      m_cur_z(0),
      m_log10(0),
      m_custom_range(0)
{
    initFromBuffer(data);
}

#define COPY_LOOP(type, data_ptr)                       \
    type *p = (type *)data;                             \
    data_t *q = data_ptr;                               \
    for (int i = 0; i < m_width*m_height*m_depth; i++)  \
        *q++ = *p++

#define COPY_LOOP_CONVERTED(type, converter, data_ptr)          \
    type *p = (type *)data;                                     \
    data_t *q = data_ptr;                                       \
    for (int i = 0; i < m_width*m_height*m_depth; i++) {        \
        *q++ = converter(*p++);                                 \
    }

LWData::LWData(int width, int height, int depth,
               const char *format, const char *data)
    : m_width(width),
      m_height(height),
      m_depth(depth),
      m_cur_z(0),
      m_log10(0),
      m_custom_range(0)
{
    // XXX currently, we interpret signed types as unsigned

    // the easy case
    if (!strcmp(format, "<u4") || !strcmp(format, "<i4") ||
        !strcmp(format, "u4")  || !strcmp(format, "i4")) {
        initFromBuffer(data);
        return;
    }

    initFromBuffer(NULL);
    if (!strcmp(format, ">I4") || !strcmp(format, ">i4")) {
        COPY_LOOP_CONVERTED(uint32_t, bswap_32, m_data);
    } else if (!strcmp(format, "<u2") || !strcmp(format, "<i2") ||
               !strcmp(format, "u2")  || !strcmp(format, "i2")) {
        COPY_LOOP(uint16_t, m_data);
    } else if (!strcmp(format, ">u2") || !strcmp(format, ">i2")) {
        COPY_LOOP_CONVERTED(uint16_t, bswap_16, m_data);
    } else if (!strcmp(format, "u1") || !strcmp(format, "i1")) {
        COPY_LOOP(uint8_t, m_data);
    } else if (!strcmp(format, "<f8") || !strcmp(format, "f8")) {
        COPY_LOOP(double, m_data);
    } else if (!strcmp(format, ">f8")) {
        COPY_LOOP_CONVERTED(double, bswap_64_float, m_data);
    } else if (!strcmp(format, "<f4") || !strcmp(format, "f4")) {
        COPY_LOOP(float, m_data);
    } else if (!strcmp(format, ">f4")) {
        COPY_LOOP_CONVERTED(float, bswap_32_float, m_data);
    } else {
        std::cerr << "Unsupported format: " << format << "!" << std::endl;
    }
    updateRange();
}


LWData::LWData(const char* filename, LWFiletype filetype)
    : m_data(NULL),
      m_clone(NULL),
      m_data_owned(false),
      m_width(0),
      m_height(0),
      m_depth(0),
      m_cur_z(0),
      m_log10(0),
      m_custom_range(0),
      m_normalized(0),
      m_darkfieldsubtracted(0),
      m_despeckled(0),
      m_filter(NoImageFilter),
      m_operation(NoImageOperation),
      m_despecklevalue(3000)
{

    if (filetype == TYPE_FITS) {
        if (! _readFits(filename)) {
            _dummyInit();
        }
    }
}

LWData::LWData(const LWData &other)
    : m_data_owned(true),
      m_width(other.m_width),
      m_height(other.m_height),
      m_depth(other.m_depth),
      m_min(other.m_min),
      m_max(other.m_max),
      m_cur_z(other.m_cur_z),
      m_log10(other.m_log10),
      m_custom_range(other.m_custom_range),
      m_range_min(other.m_range_min),
      m_range_max(other.m_range_max),
      m_normalized(other.m_normalized),
      m_darkfieldsubtracted(other.m_darkfieldsubtracted),
      m_despeckled(other.m_despeckled),
      m_filter(other.m_filter),
      m_operation(other.m_operation),
      m_despecklevalue(other.m_despecklevalue)
{
    m_data = new data_t[other.size()];
    m_clone = new data_t[other.size()];
    memcpy(m_data, other.m_data, sizeof(data_t) * other.size());
    memcpy(m_clone, other.m_clone, sizeof(data_t) * other.size());
}

LWData::~LWData()
{
    if (m_data_owned) {
        if (m_data) {
            delete[] m_data;
            m_data = NULL;
        }
        if (m_clone) {
            delete[] m_clone;
            m_clone = NULL;
        }
        m_data_owned = false;
    }
}

bool LWData::_readFits(const char *filename)
{
    fitsfile *file_pointer;    // CFITSIO file pointer, defined in fitsio.h
    int status = 0;            // CFITSIO status, must be initialized to zero
    int max_dimensions = 3;    // third dimension exists but contains only one image in our case
    int num_dimensions, bitpix, any_null, hdutype;
    float null_value = 0.;

    int x, y, total_pixel;
    long dimensions[3];

    float *float_data;
    char *data;

    if (!fits_open_file(&file_pointer, filename, READONLY, &status)) {
        if (!fits_get_img_param(file_pointer, max_dimensions, &bitpix,
                                &num_dimensions, dimensions, &status)) {
            if (fits_get_hdu_type(file_pointer, &hdutype, &status) ||
                    hdutype != IMAGE_HDU || num_dimensions != 3) {
                std::cerr << "This .fits file does not contain valid image data!" << std::endl;
                fits_close_file(file_pointer, &status);
                return false;
            } else {
                m_width  = (int) dimensions[0];
                m_height = (int) dimensions[1];
                m_depth  = (int) dimensions[2];

                total_pixel = m_height * m_width;

                float_data = (float *) malloc(total_pixel * sizeof(float));  // 32bit float values

                if (!float_data) {
                    std::cerr << "Memory allocation for data arrays failed!" << std::endl;
                    fits_close_file(file_pointer, &status);
                    return false;
                }

                data = (char *) malloc(total_pixel * sizeof(data_t));  // 32bit integer values

                if (!data) {
                    std::cerr << "Memory allocation for data arrays failed!" << std::endl;
                    free(float_data);
                    fits_close_file(file_pointer, &status);
                    return false;
                }

                if (fits_read_img(file_pointer, TFLOAT, 1, total_pixel, &null_value,
                                  float_data, &any_null, &status)) {
                    std::cerr << "Could not read image data from file for some reason!" << std::endl;
                    free(data);
                    free(float_data);
                    fits_close_file(file_pointer, &status);
                    return false;
                }

                fits_close_file(file_pointer, &status);

                for (y = 0; y < m_height; ++y)
                    for (x = 0; x < m_width; ++x)
                        data[2*x + 2*y*m_width] = (data_t)float_data[x + y*m_width];
            }
        }
    } else {
        std::cerr << "Could not open file " << filename << std::endl;
        return false;
    }

    initFromBuffer(data);
    updateRange();

    free(float_data);
    free(data);

    return true;
}

inline data_t LWData::data(int x, int y, int z) const
{
    if (m_data == NULL)
        return 0;
    if (x >= 0 && x < m_width &&
        y >= 0 && y < m_height &&
        z >= 0 && z < m_depth)
        return m_data[z*m_width*m_height + y*m_width + x];
    return 0;
}

void LWData::updateRange()
{
    m_min = std::numeric_limits<double>::max();
    m_max = 0;
    for (int y = 0; y < m_height; ++y) {
        for (int x = 0; x < m_width; ++x) {
            double v = value((double)x, (double)y);
            m_min = (m_min < v) ? m_min : v;
            m_max = (m_max > v) ? m_max : v;
        }
    }
}

double LWData::value(double x, double y) const
{
    double v = (double)data((int)x, (int)y, m_cur_z);
    if (m_log10)
        v = safe_log10(v);
    /*
    if (m_custom_range) {
        v = (v > m_range_max) ? m_range_max : v;
        v = (v < m_range_min) ? m_range_min : v;
    }
    */
    return v;
}

double LWData::valueRaw(int x, int y) const
{
    return (double)data(x, y, m_cur_z);
}

double LWData::valueRaw(int x, int y, int z) const
{
    return (double)data(x, y, z);
}

void LWData::histogram(int bins, double *xs, double *ys) const
{
    double step = (m_max - m_min) / (double)bins;
    if (step == 0)
        return;
    for (int i = 0; i < bins; ++i) {
        xs[i] = m_min + i * step + 0.5 * step;
    }
    for (int y = 0; y < m_height; ++y) {
        for (int x = 0; x < m_width; ++x) {
            ys[(int)((value(x, y) - m_min) / step)]++;
        }
    }
}

void LWData::histogram(int bins, QVector<double> **xs, QVector<double> **ys) const
{
    *xs = new QVector<double>(bins);
    *ys = new QVector<double>(bins + 1);
    double step = (m_max - m_min) / (double)bins;
    if (step == 0)
        return;
    for (int i = 0; i < bins; ++i) {
        (**xs)[i] = m_min + i * step + 0.5 * step;
    }
    for (int y = 0; y < m_height; ++y) {
        for (int x = 0; x < m_width; ++x) {
            (**ys)[(int)((value(x, y) - m_min) / step)]++;
        }
    }
    (**ys)[bins-1] += (**ys)[bins];
    (*ys)->pop_back();
}

void LWData::setCurrentZ(int val)
{
    if (val < 0 || val >= m_depth) {
        std::cerr << "invalid current Z selected" << std::endl;
        return;
    }
    m_cur_z = val;
    updateRange();
}

void LWData::setLog10(bool val)
{
    if (m_log10 != val) {
        if (m_custom_range) {
            if (val) {
                m_range_min = safe_log10(m_range_min);
                m_range_max = safe_log10(m_range_max);
            } else {
                m_range_min = exp10(m_range_min);
                m_range_max = exp10(m_range_max);
            }
        }
        m_log10 = val;
        updateRange();
    }
}

void LWData::setDespeckled(bool val)
{
    if (m_despeckled == val)
        return;
    m_despeckled = val;

    if (m_despeckled) {
        CLOCK_START();
        float *pdata = (float *)malloc(size() * sizeof(float));
        for (int i = 0; i < size(); ++i)
            pdata[i] = (float)m_data[i];
        CLOCK_STOP("malloc and copy");

        CLOCK_START();
        LWImageProc::despeckleFilter(pdata, m_despecklevalue, m_width, m_height);
        CLOCK_STOP("despeckle filter");

        CLOCK_START();
        for (int i = 0; i < size(); ++i)
            m_data[i] = (data_t)pdata[i];
        CLOCK_STOP("copy back to data");

        free(pdata);
    } else {
        memcpy(m_data, m_clone, sizeof(data_t) * size());
    }
    updateRange();
}

void LWData::setNormalized(bool val)
{
    if (m_normalized == val)
        return;
    m_normalized = val;

    if (m_normalized) {
        float *pdata = (float *)malloc(size() * sizeof(float));
        for (int i = 0; i < size(); ++i)
            pdata[i] = (float)m_data[i];

        CLOCK_START();
        // XXX file name shouldn't be hardcoded :)
        LWData openbeam("data/openbeam/ob_hd_1.fits", TYPE_FITS);
        float *sdata = (float *)malloc(size() * sizeof(float));
        for (int i = 0; i < size(); ++i)
            sdata[i] = openbeam.buffer()[i];
        CLOCK_STOP("load openbeam image");

        CLOCK_START();
        LWImageProc::pixelwiseDivideImages(pdata, sdata, m_width, m_height);
        CLOCK_STOP("pixelwise divide images");

        for (int i = 0; i < size(); ++i)
            m_data[i] = (data_t)pdata[i];

        free(pdata);
        free(sdata);
        updateRange();
    } else {
        CLOCK_START();
        memcpy(m_data, m_clone, sizeof(data_t) * size());
        CLOCK_STOP("restore original from memory");

        CLOCK_START();
        updateRange();
        CLOCK_STOP("updateRange() function");
    }
}

void LWData::setDarkfieldSubtracted(bool val)
{
    if (m_darkfieldsubtracted == val)
        return;
    m_darkfieldsubtracted = val;

    if (m_darkfieldsubtracted) {
        float *pdata = (float *)malloc(size() * sizeof(float));
        for (int i = 0; i < size(); ++i)
            pdata[i] = (float)m_data[i];

        CLOCK_START();
        // XXX file name shouldn't be hardcoded :)
        LWData darkfield("data/darkimage/di_hd_1.fits", TYPE_FITS);
        float *sdata = (float *)malloc(size() * sizeof(float));
        for (int i = 0; i < size(); ++i)
            sdata[i] = darkfield.buffer()[i];
        CLOCK_STOP("load darkfield image");

        CLOCK_START();
        LWImageProc::pixelwiseSubtractImages(pdata, sdata, m_width, m_height);
        CLOCK_STOP("pixelwise subtract images");

        for (int i = 0; i < size(); ++i)
            m_data[i] = (data_t)pdata[i];

        free(pdata);
        free(sdata);
        updateRange();
    } else {
        CLOCK_START();
        memcpy(m_data, m_clone, sizeof(data_t) * size());
        CLOCK_STOP("restore original from memory");

        CLOCK_START();
        updateRange();
        CLOCK_STOP("updateRange() function");
    }
}

void LWData::setDespeckleValue(float value)
{
    if (m_despecklevalue == value)
        return;
    m_despecklevalue = value;

    memcpy(m_data, m_clone, sizeof(data_t) * size());

    float *pdata = (float *)malloc(size() * sizeof(float));
    for (int i = 0; i < size(); ++i)
        pdata[i] = (float)m_data[i];

    LWImageProc::despeckleFilter(pdata, m_despecklevalue, m_width, m_height);

    for (int i = 0; i < size(); ++i)
        m_data[i] = (data_t)pdata[i];

    free(pdata);

    updateRange();
}

void LWData::setImageFilter(LWImageFilters which)
{
    if (m_filter == which)
        return;

    m_filter = which;
    if (m_filter == NoImageFilter) {
        memcpy(m_data, m_clone, sizeof(data_t) * size());
    } else {
        float *pdata = (float*)malloc(size() * sizeof(float));

        for (int i=0; i<size(); ++i)
            pdata[i] = (float)m_data[i];

        if (m_filter == MedianFilter) {
            LWImageProc::medianFilter(pdata, m_width, m_height);
        } else if (m_filter == HybridMedianFilter) {
            LWImageProc::hybridmedianFilter(pdata, m_width, m_height);
        } else if (m_filter == DespeckleFilter) {
            LWImageProc::despeckleFilter(pdata, m_despecklevalue, m_width, m_height);
        }

        for (int i = 0; i < size(); ++i)
            m_data[i] = (data_t)pdata[i];

        free(pdata);
    }
    updateRange();
}

void LWData::setImageOperation(LWImageOperations which)
{
    if (m_operation == which)
        return;

    m_operation = which;
    if (m_operation == NoImageOperation) {
        memcpy(m_data, m_clone, sizeof(data_t) * size());
    } else {
        float *pdata = (float *)malloc(size() * sizeof(float));
        float *sdata = (float *)malloc(size() * sizeof(float));

        for (int i = 0; i < size(); ++i)
            pdata[i] = (float)m_data[i];

        if (m_operation == StackAverage) {
            str_vec myList;
            myList.push_back("data/test1.fits");
            myList.push_back("data/test2.fits");
            myList.push_back("data/raw/hd_000.000.fits");

            LWImageProc::pixelwiseAverage(pdata, myList, m_width, m_height);
        } else if (m_operation == OpenBeamNormalization) {

            // if not already existing: create average
            // of all openbeam images in the corresponding directory

            LWData openbeam("data/openbeam/ob_hd_1.fits", TYPE_FITS);
            for (int i = 0; i < size(); ++i)
                sdata[i] = openbeam.buffer()[i];
            LWImageProc::pixelwiseDivideImages(pdata, sdata, m_width, m_height);
        } else if (m_operation == DarkImageSubtraction) {

            // if not already existing: create average
            // of all darkfield images in the corresponding directory

            LWData darkimage("data/darkimage/di_hd_1.fits", TYPE_FITS);
            for (int i = 0; i < size(); ++i)
                sdata[i] = darkimage.buffer()[i];
            LWImageProc::pixelwiseSubtractImages(pdata, sdata, m_width, m_height);
        }

        for (int i = 0; i < size(); ++i)
            m_data[i] = (data_t)pdata[i];

        free(pdata);
    }
    updateRange();
}


double LWData::customRangeMin() const
{
    if (m_custom_range)
        return m_range_min;
    return m_min;
}

double LWData::customRangeMax() const
{
    if (m_custom_range)
        return m_range_max;
    return m_max;
}

void LWData::setCustomRange(double lower, double upper)
{
    if (lower == 0 && upper == 0) {
        m_custom_range = false;
    } else {
        m_custom_range = true;
        m_range_min = (lower < upper) ? lower : upper;
        m_range_max = (lower < upper) ? upper : lower;
    }
    updateRange();
}



void LWData::saveAsFitsImage(float *data, char *fits_filename)
{
    long 		 dimensions[2] = {m_width, m_height};
    fitsfile    *ffptr;
    int 		 status = 0;
    int          exists = 0;

    if (fits_file_exists(fits_filename, &exists, &status)) {
        if (fits_create_file(&ffptr, fits_filename, &status))
            std::cerr << "doesn't exist but still couldn't create file" << std::endl;
    } else {
        // XXX doesn't belong here, LWData is not supposed to use GUI
/*        switch (QMessageBox::warning(NULL, "Replace file?",
                                     "Do you want to replace \n" + (QString)fits_filename, "&Yes", "&No") )
        {
            case 0:
                if (fits_open_file(&ffptr, fits_filename, READWRITE, &status))
                    std::cerr << "couldn't open file" << std::endl;
                if (fits_delete_file(ffptr, &status))
                    std::cerr << "couldn't delete existing file" << std::endl;
                if (fits_create_file(&ffptr, fits_filename, &status))
                    std::cerr << "couldn't create file" << std::endl;
                break;

            default:
                break;
        }
*/
    }

    if (fits_create_img(ffptr, 32, 2, dimensions, &status))
        std::cerr << "couldn't add image table" << std::endl;

    if (fits_write_img(ffptr, TFLOAT, 1, 2048*2048, data, &status))
        std::cerr << "couldn't write data" << std::endl;

    fits_close_file(ffptr, &status);

    if (status)
        fits_report_error(stderr, status);   // print any cfitsio error message
}
