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


LWData::LWData()
    : QwtRasterData(QwtDoubleRect(0, 0, 0, 0)),
      m_log10(0)
{
    m_data = new data_t[0];
}

LWData::LWData(int width, int height, int depth, data_t *data)
    : QwtRasterData(QwtDoubleRect(0, width, 0, height)),
      m_width(width),
      m_height(height),
      m_depth(depth),
      m_log10(0),
      m_cur_z(0)
{
    if (data) {
        m_data = data;
        updateRange();
    } else {
        m_data = new data_t[size()];
        if (m_data == NULL) {
            std::cerr << "could not allocate memory for data" << std::endl;
            return;
        }
        memset(m_data, 0, sizeof(data_t) * size());
        m_min = m_max = 0;
    }
}

LWData::LWData(const LWData &other)
    : QwtRasterData(QwtDoubleRect(other.boundingRect())),
      m_data_owned(true),
      m_width(other.m_width),
      m_height(other.m_height),
      m_depth(other.m_depth),
      m_min(other.m_min),
      m_max(other.m_max),
      m_log10(other.m_log10),
      m_cur_z(other.m_cur_z)
{
    m_data = new data_t[other.size()];
    if (m_data == NULL) {
        std::cerr << "could not allocate memory for data" << std::endl;
        return;
    }
    memcpy(m_data, other.m_data, sizeof(data_t) * other.size());
}

LWData::~LWData()
{
    if (m_data)
        delete m_data;
}

LWData::LWData(const QwtDoubleRect &rect)
    : QwtRasterData(rect),
      m_data_owned(true),
      m_width(rect.width()),
      m_height(rect.height()),
      m_depth(1),
      m_min(0),
      m_max(0),
      m_log10(0),
      m_cur_z(0)
{
    m_data = new data_t[size()];
    if (m_data == NULL) {
        std::cerr << "could not allocate memory for data" << std::endl;
        return;
    }
    memset(m_data, 0, sizeof(data_t) * size());
}

QwtRasterData *LWData::copy() const
{
    return new LWData(*this);
}

data_t LWData::data(int x, int y, int z) const
{
    if (m_data == NULL)
        return 0;
    if (x >= 0 && x < m_width &&
        y >= 0 && y < m_height &&
        z >= 0 && z < m_depth)
        return m_data[z*m_width*m_height + y*m_width + x];
    return 0;
}

void LWData::setLog10(bool val)
{
    m_log10 = val;
    updateRange();
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

QwtDoubleInterval LWData::range() const
{
    if (m_data == NULL)
        return QwtDoubleInterval(0., 1.);

    if (m_log10) {
        return QwtDoubleInterval(m_min > 0 ? log10(m_min) : -1,
                                 m_max > 0 ? log10(m_max) : -1);
    } else {
        return QwtDoubleInterval(m_min, m_max);
    }
}

void LWData::updateRange()
{
    m_min = std::numeric_limits<data_t>::max();
    m_max = 0;
    for (int y = 0; y < m_height; ++y) {
        for (int x = 0; x < m_width; ++x) {
            data_t v = data(x, y, m_cur_z);
            m_min = (m_min < v) ? m_min : v;
            m_max = (m_max > v) ? m_max : v;
        }
    }
}

double LWData::value(double x, double y) const
{
    double v = (double)data((int)x, (int)y, m_cur_z);
    if (m_log10) {
        return (v > 0.) ? log10(v) : -1;
    } else {
        return v;
    }
}

double LWData::valueRaw(int x, int y) const
{
    return (double)data(x, y, m_cur_z);
}

double LWData::valueRaw(int x, int y, int z) const
{
    return (double)data(x, y, z);
}
