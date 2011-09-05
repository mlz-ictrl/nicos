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

#include <QGridLayout>

#include "lw_widget.h"


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

LWPlot::LWPlot(QWidget *parent) : QwtPlot(parent), m_spectro(0),
                                  m_panner(0), m_picker(0), m_zoomer(0)
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

    changeRange();

    plotLayout()->setAlignCanvasToScales(true);

    m_zoomer = new LWZoomer(canvas(), m_spectro);
    m_panner = new QwtPlotPanner(canvas());
    m_panner->setAxisEnabled(QwtPlot::yRight, false);
    m_panner->setMouseButton(Qt::MidButton);
    //m_picker = new QwtPlotPicker(QwtPlot::xBottom, QwtPlot::yLeft,
    //                             QwtPicker::RectSelection,
    //                             QwtPlotPicker::RectRubberBand,
    //                             QwtPicker::AlwaysOff, canvas());
    //m_picker->setMousePattern(QwtEventPattern::MouseSelect1, Qt::MidButton);
    //m_picker->setRubberBandPen(QColor(Qt::green));

    QFontMetrics fm(axisWidget(QwtPlot::yLeft)->font());
    axisScaleDraw(QwtPlot::yLeft)->setMinimumExtent(fm.width("100."));
}

void LWPlot::deinitPlot()
{
    if (m_zoomer) { delete m_zoomer; m_zoomer = 0; }
    if (m_panner) { delete m_panner; m_panner = 0; }
    if (m_spectro) { delete m_spectro; m_spectro = 0; }
}

void LWPlot::changeRange()
{
    LWRasterData &data = (LWRasterData &)m_spectro->data();

    QwtDoubleInterval range = data.range();
    setAxisScale(QwtPlot::yRight, range.minValue(), range.maxValue());
    axisWidget(QwtPlot::yRight)->setColorMap(data.range(),
                                             m_spectro->colorMap());
    
    setAxisScale(QwtPlot::yLeft, 0, data.height());
    setAxisScale(QwtPlot::xBottom, 0, data.width());
}

void LWPlot::setData(QwtRasterData* data)
{
    if (!m_spectro)
        return;
    m_spectro->setData(*data);
    changeRange();
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


/** LWWidget ******************************************************************/

LWWidget::LWWidget(QWidget *parent) : QWidget(parent),
                                      m_data(NULL)
{
    m_plot = new LWPlot(this);
    setColorMap(false, false);

    QGridLayout *grid = new QGridLayout(this);
    grid->addWidget(m_plot, 0, 0, 1, 1);
    this->setLayout(grid);
}

LWWidget::~LWWidget()
{
    unload();
}

void LWWidget::unload()
{
    if (m_data) {
        delete m_data;
        m_data = NULL;
    }
}

void LWWidget::setData(LWData *data)
{
    if (m_data)
        unload();
    m_data = data;
    updateGraph();
    m_plot->getZoomer()->setZoomBase();
}   

void LWWidget::setLog10(bool val)
{
    if (m_data) {
        m_data->setLog10(val);
        updateGraph();
    }
}

void LWWidget::setColorMap(bool greyscale, bool cyclic)
{
    if (greyscale) {
        QwtLinearColorMap colorMap(Qt::black, Qt::white);
        m_plot->setColorMap(colorMap);
    } else {
        if (cyclic) {
            // e.g. for phase (0..2pi) display
            QwtLinearColorMap colorMap(Qt::blue, Qt::blue);
            colorMap.addColorStop(0.0, Qt::blue);
            colorMap.addColorStop(0.75, Qt::red);
            colorMap.addColorStop(0.5, Qt::yellow);
            colorMap.addColorStop(0.25, Qt::cyan);
            colorMap.addColorStop(1.0, Qt::blue);
            m_plot->setColorMap(colorMap);
        } else {
            QwtLinearColorMap colorMap(Qt::blue, Qt::red);
            colorMap.addColorStop(0.0, Qt::blue);
            colorMap.addColorStop(0.33, Qt::cyan);
            colorMap.addColorStop(0.66, Qt::yellow);
            colorMap.addColorStop(1.0, Qt::red);
            m_plot->setColorMap(colorMap);
        }
    }
    updateGraph();
}

void LWWidget::setColormapGray(bool val)
{
    setColorMap(val, false);
}

void LWWidget::setColormapCyclic(bool val)
{
    setColorMap(false, val);
}

void LWWidget::setCustomRange(double lower, double upper)
{
    if (m_data) {
        m_data->setCustomRange(lower, upper);
        updateGraph();
    }
}

void LWWidget::setCustomRangeMin(int lower)
{
    if (m_data) {
        m_data->setCustomRange((data_t)lower, m_data->customRangeMax());
        updateGraph();
    }
}

void LWWidget::setCustomRangeMax(int upper)
{
    if (m_data) {
        m_data->setCustomRange(m_data->customRangeMin(), (data_t)upper);
        updateGraph();
    }
}

void LWWidget::updateGraph()
{
    if (m_data) {
        m_plot->setData(new LWRasterData(m_data));
        m_plot->replot();
        updateLabels();
    }
}

void LWWidget::updateLabels()
{
    if (m_data)
        m_plot->axisWidget(QwtPlot::yRight)->setTitle(
            m_data->isLog10() ? "log Counts" : "Counts");
}
