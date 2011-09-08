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

#include "lw_plot.h"


/** LWZoomer ******************************************************************/

LWZoomer::LWZoomer(QwtPlotCanvas *canvas, const QwtPlotSpectrogram *spectro)
    : QwtPlotZoomer(canvas), m_spectro(spectro)
{
    setSelectionFlags(QwtPicker::RectSelection | QwtPicker::DragSelection);

    setMousePattern(QwtEventPattern::MouseSelect2, Qt::RightButton,
                    Qt::ControlModifier);
    setMousePattern(QwtEventPattern::MouseSelect3, Qt::RightButton);

    QColor blue(Qt::darkBlue);
    setRubberBandPen(blue);
    setTrackerPen(blue);

    setTrackerMode(AlwaysOn);
}

LWZoomer::~LWZoomer()
{}

void LWZoomer::setKeepAspect(bool val)
{
    m_aspect = val;
}

void LWZoomer::zoom(const QwtDoubleRect &rect)
{
    QwtDoubleRect current = zoomRect();
    double old_aspect = current.height() / current.width();
    double new_aspect = rect.height() / rect.width();
    if (m_aspect && old_aspect != new_aspect) {
        QwtDoubleRect adjusted = QwtDoubleRect(rect);
        if (old_aspect < new_aspect)
            adjusted.setWidth(adjusted.height() / old_aspect);
        else {
            // setHeight changes bottom edge, we want top
            adjusted.setTop(adjusted.bottom() -
                            adjusted.width() * old_aspect);
        }
        QwtPlotZoomer::zoom(adjusted);
        return;
    }
    QwtPlotZoomer::zoom(rect);
}

QwtText LWZoomer::trackerText(const QwtDoublePoint &pos) const
{
    QString str = "Pixel: ";
    str += QString::number(int(pos.x()));
    str += ", ";
    str += QString::number(int(pos.y()));

    const LWRasterData &data = (const LWRasterData &)m_spectro->data();

    str += "\nValue: ";
    str += QString::number(data.valueRaw(pos.x(), pos.y()));

    QwtText text = str;
    QColor bg(Qt::white);
    bg.setAlpha(200);
    text.setBackgroundBrush(QBrush(bg));
    return text;
}


/** LWPlot *********************************************************************/

LWPlot::LWPlot(QWidget *parent) : QwtPlot(parent), m_spectro(0), m_panner(0),
                                  m_picker(0), m_rescaler(0), m_zoomer(0),
                                  m_scale_width(0), m_scale_height(0)
{
    initPlot();
}

LWPlot::~LWPlot()
{
    deinitPlot();
}

void LWPlot::initPlot()
{
    deinitPlot();

    axisWidget(QwtPlot::xBottom)->setTitle("x Pixels");
    axisWidget(QwtPlot::yLeft)->setTitle("y Pixels");

    m_spectro = new QwtPlotSpectrogram();
    m_spectro->setData(LWRasterData());   // dummy object
    m_spectro->setDisplayMode(QwtPlotSpectrogram::ImageMode, true);
    m_spectro->setDisplayMode(QwtPlotSpectrogram::ContourMode, false);
    m_spectro->attach(this);

    setCanvasBackground(Qt::white);

    enableAxis(QwtPlot::yRight);
    axisWidget(QwtPlot::yRight)->setColorBarEnabled(true);

    updateRange();

    plotLayout()->setAlignCanvasToScales(true);

    m_zoomer = new LWZoomer(canvas(), m_spectro);
    m_panner = new QwtPlotPanner(canvas());
    m_panner->setAxisEnabled(QwtPlot::yRight, false);
    m_panner->setMouseButton(Qt::MidButton);
    m_picker = new QwtPlotPicker(QwtPlot::xBottom, QwtPlot::yLeft,
                                 QwtPicker::PolygonSelection,
                                 QwtPlotPicker::PolygonRubberBand,
                                 QwtPicker::AlwaysOff, canvas());
    m_picker->setRubberBandPen(QColor(Qt::green));
    m_picker->setEnabled(false);
    //m_rescaler = new QwtPlotRescaler(canvas(), QwtPlot::xBottom,
    //                                 QwtPlotRescaler::Fitting);

    QFontMetrics fm(axisWidget(QwtPlot::yLeft)->font());
    axisScaleDraw(QwtPlot::yLeft)->setMinimumExtent(fm.width("100."));
}

void LWPlot::deinitPlot()
{
    if (m_zoomer) { delete m_zoomer; m_zoomer = 0; }
    if (m_panner) { delete m_panner; m_panner = 0; }
    if (m_picker) { delete m_picker; m_picker = 0; }
    if (m_rescaler) { delete m_rescaler; m_rescaler = 0; }
    if (m_spectro) { delete m_spectro; m_spectro = 0; }
}

void LWPlot::updateRange()
{
    LWRasterData &data = (LWRasterData &)m_spectro->data();

    QwtDoubleInterval range = data.range();
    setAxisScale(QwtPlot::yRight, range.minValue(), range.maxValue());
    axisWidget(QwtPlot::yRight)->setColorMap(data.range(),
                                             m_spectro->colorMap());

    if (data.width() != m_scale_width) {
        m_scale_width = data.width();
        setAxisScale(QwtPlot::xBottom, 0, m_scale_width);
    }
    if (data.height() != m_scale_height) {
        m_scale_height = data.height();
        setAxisScale(QwtPlot::yLeft, 0, m_scale_height);
    }
}

void LWPlot::setData(QwtRasterData* data)
{
    if (!m_spectro)
        return;
    m_spectro->setData(*data);
    updateRange();
    replot();
}

void LWPlot::setColorMap(QwtColorMap &map)
{
    if (!m_spectro)
        return;
    m_spectro->setColorMap(map);
}

void LWPlot::printPlot()
{
    QPrinter printer;
    printer.setOrientation(QPrinter::Landscape);
    QPrintDialog dialog(&printer);
    if (dialog.exec())
        print(printer);
}

