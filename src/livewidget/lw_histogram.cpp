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
//   Josef Wilgen, Uwe Rathmann (authors of Qwt example code)
//   Tobias Weber <tobias.weber@frm2.tum.de>
//   Georg Brandl <georg.brandl@frm2.tum.de>
//
// *****************************************************************************

#include <QPainter>

#include <qwt_plot.h>
#include <qwt_interval_data.h>
#include <qwt_painter.h>
#include <qwt_scale_map.h>

#include "lw_histogram.h"


class LWHistogramItem::PrivateData
{
  public:
    QwtCPointerData *data;
    QColor color;
    double reference;
};

LWHistogramItem::LWHistogramItem(const QwtText &title) :
    QwtPlotItem(title)
{
    init();
}

LWHistogramItem::LWHistogramItem(const QString &title) :
    QwtPlotItem(QwtText(title))
{
    init();
}

LWHistogramItem::~LWHistogramItem()
{
    delete d_data;
}

void LWHistogramItem::init()
{
    d_data = new PrivateData();
    d_data->reference = 0.0;

    setItemAttribute(QwtPlotItem::AutoScale, true);
    setItemAttribute(QwtPlotItem::Legend, true);

    setZ(20.0);
}

void LWHistogramItem::setBaseline(double reference)
{
    if (d_data->reference != reference) {
        d_data->reference = reference;
        itemChanged();
    }
}

double LWHistogramItem::baseline() const
{
    return d_data->reference;
}

void LWHistogramItem::setData(const QwtCPointerData &data)
{
    d_data->data = new QwtCPointerData(data);
    itemChanged();
}

const QwtCPointerData &LWHistogramItem::data() const
{
    return *d_data->data;
}

void LWHistogramItem::setColor(const QColor &color)
{
    if (d_data->color != color) {
        d_data->color = color;
        itemChanged();
    }
}

QColor LWHistogramItem::color() const
{
    return d_data->color;
}

QwtDoubleRect LWHistogramItem::boundingRect() const
{
    QwtDoubleRect rect = d_data->data->boundingRect();
    if (!rect.isValid())
        return rect;

    if (rect.bottom() < d_data->reference)
        rect.setBottom(d_data->reference);
    else if (rect.top() > d_data->reference)
        rect.setTop(d_data->reference);

    return rect;
}

int LWHistogramItem::rtti() const
{
    return QwtPlotItem::Rtti_PlotHistogram;
}

void LWHistogramItem::draw(QPainter *painter, const QwtScaleMap &xMap,
                           const QwtScaleMap &yMap, const QRect &) const
{
    const QwtCPointerData *data = d_data->data;

    painter->save();
    painter->setBrush(d_data->color);

    const int y0 = yMap.transform(baseline());

    for (int i = 0; i < (int)data->size() - 1; i++) {
        const int y2 = yMap.transform(data->y(i));
        if (y2 == y0)
            continue;

        int x1 = xMap.transform(data->x(i));
        int x2 = xMap.transform(data->x(i+1));
        if (x1 > x2)
            qSwap(x1, x2);

        QwtPainter::drawRect(painter, x1, y0, x2 - x1, y2 - y0);
    }
    painter->restore();
}
