// *****************************************************************************
// Module:
//   $Id$
//
// Author:
//   Tobias Weber <tobias.weber@frm2.tum.de>
//   Georg Brandl <georg.brandl@frm2.tum.de>
//
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
// *****************************************************************************

#include <assert.h>
#include <iostream>
#include <limits>
#include <math.h>

#include "lw_data.h"

static inline double safe_log10(double v)
{
    v = (v > 0.) ? log10(v) : -1;
    if (v != v) v = -1.;
    return v;
}

static inline uint16_t bswap_16(uint16_t x) {
    return (x << 8) | (x >> 8);
}

static inline uint32_t bswap_32(uint32_t x) {
    return (bswap_16(x & 0xFFFF) << 16) | bswap_16(x >> 16);
}


/** LWData ********************************************************************/

LWData::LWData()
    : m_log10(0),
      m_custom_range(0)
{
    m_data = new data_t[0];
    m_data_owned = true;
}

void LWData::initFromBuffer(const char *data)
{
    m_data = new data_t[size()];
    m_data_owned = true;
    if (m_data == NULL) {
        std::cerr << "could not allocate memory for data" << std::endl;
        return;
    }
    if (data) {
        memcpy(m_data, data, sizeof(data_t) * size());
        updateRange();
    } else {
        memset(m_data, 0, sizeof(data_t) * size());
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

#define COPY_LOOP(type)                           \
    type *p = (type *)data;                       \
    data_t *q = m_data;                           \
    for (int i = 0; i < width*height*depth; i++)  \
        *q++ = *p++

#define COPY_LOOP_CONVERTED(type, converter)            \
    type *p = (type *)data;                             \
    data_t *q = m_data;                                 \
    for (int i = 0; i < width*height*depth; i++) {      \
        *q++ = converter(*p++);                         \
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
    if (!strcmp(format, "<I4") || !strcmp(format, "<i4")) {
        initFromBuffer(data);
        return;
    }

    initFromBuffer(NULL);
    if (!strcmp(format, ">I4") || !strcmp(format, ">i4")) {
        COPY_LOOP_CONVERTED(uint32_t, bswap_32);
    } else if (!strcmp(format, "<I2") || !strcmp(format, "<i2")) {
        COPY_LOOP(uint16_t);
    } else if (!strcmp(format, ">I2") || !strcmp(format, ">i2")) {
        COPY_LOOP_CONVERTED(uint16_t, bswap_16);
    } else if (!strcmp(format, "I1") || !strcmp(format, "i1")) {
        COPY_LOOP(uint8_t);
    } else if (!strcmp(format, "f8")) {
        COPY_LOOP(double);
    } else if (!strcmp(format, "f4")) {
        COPY_LOOP(float);
    } else {
        std::cerr << "Unsupported format: " << format << "!" << std::endl;
    }
    updateRange();
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
      m_range_max(other.m_range_max)
{
    m_data = new data_t[other.size()];
    memcpy(m_data, other.m_data, sizeof(data_t) * other.size());
}

LWData::~LWData()
{
    if (m_data && m_data_owned)
        delete m_data;
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
    m_min = std::numeric_limits<data_t>::max();
    m_max = 0;
    for (int y = 0; y < m_height; ++y) {
        for (int x = 0; x < m_width; ++x) {
            data_t v = value((double)x, (double)y);
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
    if (m_custom_range) {
        v = (v > m_range_max) ? m_range_max : v;
        v = (v < m_range_min) ? m_range_min : v;
    }
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

void LWData::histogram(int bins, data_t *out, double *step) const
{
    *step = (m_max - m_min) / (double)bins;
    for (int y = 0; y < m_height; ++y) {
        for (int x = 0; x < m_width; ++x) {
            out[(int)((data(x, y, m_cur_z) - m_min) / *step)]++;
        }
    }
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
                m_range_min = (data_t)exp10(m_range_min);
                m_range_max = (data_t)exp10(m_range_max);
            }
        }
        m_log10 = val;
        updateRange();
    }
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
