// *****************************************************************************
// NICOS, the Networked Instrument Control System of the FRM-II
// Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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
//
// *****************************************************************************

#ifndef LW_DATA_H
#define LW_DATA_H

#include <stdint.h>

#include <qwt_plot_spectrogram.h>

#include "lw_common.h"

// undefine to remove timing console messages
#define CLOCKING

// data type used for single pixel count values
typedef uint32_t data_t;


class LWData
{
  private:
    virtual void updateRange();
    virtual void initFromBuffer(const char *data);
    void _dummyInit();
    bool _readFits(const char *filename);

  protected:
    // concerning the data
    data_t *m_data;   // processed data
    data_t *m_clone;  // original data without filters/processing applied
    bool m_data_owned;
    int m_width, m_height, m_depth;
    double m_min, m_max;

    // concerning the display
    int m_cur_z;
    bool m_log10;
    bool m_custom_range;
    double m_range_min, m_range_max;

    // image filtering and processing
    bool m_normalized;
    bool m_darkfieldsubtracted;
    bool m_despeckled;
    LWImageFilters m_filter;
    LWImageOperations m_operation;
    float m_despecklevalue;

    data_t data(int x, int y, int z) const;
    int size() const { return m_width * m_height * m_depth; }

  public:
    LWData();
    LWData(int width, int height, int depth, const char *data);
    LWData(int width, int height, int depth, const char *format, const char *data);
    LWData(const char* filename, LWFiletype filetype);
    LWData(const LWData &other);

    virtual ~LWData();

    const data_t *buffer() const { return m_data; }
    const data_t *buffer_clone() const { return m_clone; }

    int width() const { return m_width; }
    int height() const { return m_height; }
    int depth() const { return m_depth; }
    double min() const { return m_min; }
    double max() const { return m_max; }

    int currentZ() const { return m_cur_z; }
    virtual void setCurrentZ(int val);

    bool isLog10() const { return m_log10; }
    virtual void setLog10(bool val);

    bool isNormalized() const { return m_normalized; }
    virtual void setNormalized(bool val);
    bool isDarkfieldSubtracted() const { return m_darkfieldsubtracted; }
    virtual void setDarkfieldSubtracted(bool val);
    bool isDespeckled() const { return m_despeckled; }
    virtual void setDespeckled(bool val);

    virtual void setDespeckleValue(float value);

    LWImageFilters isImageFilter() const { return m_filter; }
    virtual void setImageFilter(LWImageFilters which);

    LWImageOperations isImageOperation() const { return m_operation; }
    virtual void setImageOperation(LWImageOperations which);

    void saveAsFitsImage(float *data, char *fits_filename);

    bool hasCustomRange() const { return m_custom_range; }
    double customRangeMin() const;
    double customRangeMax() const;
    virtual void setCustomRange(double lower, double upper);

    /// Get current presentation value at the specified point.
    virtual double value(double x, double y) const;
    /// Get raw value without regard to presentation settings (like log10).
    virtual double valueRaw(int x, int y) const;
    /// Same, but also specifying the layer.
    virtual double valueRaw(int x, int y, int z) const;

    /// Create a histogram of the current layer.  Caller must allocate
    /// the xs and ys arrays with a length of "bins".
    virtual void histogram(int bins, double *xs, double *ys) const;
    /// Same, but creates QVectors of doubles (callable from Python).
    virtual void histogram(int bins, QVector<double> **xs,
                           QVector<double> **ys) const;

};


class LWRasterData : public QwtRasterData
{
  private:
    const LWData *m_data;

  public:
    LWRasterData() :
        QwtRasterData(QwtDoubleRect(0, 1, 0, 1)),
        m_data(new LWData()) {
    }
    LWRasterData(const LWData *data) :
        QwtRasterData(QwtDoubleRect(0, data->width(), 0, data->height())),
        m_data(data) {
    }
    LWRasterData(const LWRasterData &other) :
        QwtRasterData(other), m_data(other.m_data) {
    }

    // QwtRasterData overridables
    virtual QwtRasterData *copy() const {
        return new LWRasterData(*this);
    }
    virtual QwtDoubleInterval range() const {
        if (m_data->hasCustomRange()) {
            return QwtDoubleInterval(m_data->customRangeMin(),
                                     m_data->customRangeMax());
        } else {
            return QwtDoubleInterval(m_data->min(), m_data->max());
        }
    }
    virtual double value(double x, double y) const {
        return m_data->value(x, y);
    }
    virtual double valueRaw(double x, double y) const {
        return m_data->valueRaw(x, y);
    }

    int width() {
        return m_data->width();
    }
    int height() {
        return m_data->height();
    }
};

#endif
