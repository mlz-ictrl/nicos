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

LWZoomer::LWZoomer(QwtPlotCanvas *canvas, const QwtPlotSpectrogram *pData)
    : QwtPlotZoomer(canvas), m_pData(pData)
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

    const LWData &data = (const LWData &)m_pData->data();

    str += "\nValue: ";
    str += QString::number(data.valueRaw(pos.x(), pos.y()));

    QwtText text = str;
    QColor bg(Qt::white);
    bg.setAlpha(200);
    text.setBackgroundBrush(QBrush(bg));
    return text;
}


/** LWPanner ******************************************************************/

LWPanner::LWPanner(QwtPlotCanvas *canvas) : QwtPlotPanner(canvas)
{
    setAxisEnabled(QwtPlot::yRight, false);
    setMouseButton(Qt::MidButton);
}

LWPanner::~LWPanner()
{}


/** LWPlot *********************************************************************/

LWPlot::LWPlot(QWidget *parent) : QwtPlot(parent), m_spectro(0),
                                  m_zoomer(0), m_panner(0)
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
    m_spectro->setData(LWData());   // dummy object
    m_spectro->setDisplayMode(QwtPlotSpectrogram::ImageMode, true);
    m_spectro->setDisplayMode(QwtPlotSpectrogram::ContourMode, false);
    m_spectro->attach(this);

    setCanvasBackground(Qt::white);
    setColorMap(true, false);

    enableAxis(QwtPlot::yRight);
    axisWidget(QwtPlot::yRight)->setColorBarEnabled(true);

    changeRange();

    plotLayout()->setAlignCanvasToScales(true);

    m_zoomer = new LWZoomer(canvas(), m_spectro);
    m_panner = new LWPanner(canvas());

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
    setAxisScale(QwtPlot::yRight, m_spectro->data().range().minValue(),
                 m_spectro->data().range().maxValue());
    axisWidget(QwtPlot::yRight)->setColorMap(m_spectro->data().range(),
                                             m_spectro->colorMap());

    LWData &data = (LWData &)m_spectro->data();
    
    setAxisScale(QwtPlot::yLeft, 0, data.height());
    setAxisScale(QwtPlot::xBottom, 0, data.width());
}

void LWPlot::setData(QwtRasterData* data)
{
    if (!data) return;
    m_spectro->setData(*data);
    changeRange();
}

void LWPlot::setColorMap(bool greyscale, bool cyclic)
{
    if (m_spectro == NULL)
        return;

    if (greyscale) {
        QwtLinearColorMap colorMap(Qt::black, Qt::white);
        m_spectro->setColorMap(colorMap);
    } else {
        if (cyclic) {
            // e.g. for phase (0..2pi) display
            QwtLinearColorMap colorMap(Qt::blue, Qt::blue);
            colorMap.addColorStop(0.0, Qt::blue);
            colorMap.addColorStop(0.75, Qt::red);
            colorMap.addColorStop(0.5, Qt::yellow);
            colorMap.addColorStop(0.25, Qt::cyan);
            colorMap.addColorStop(1.0, Qt::blue);
            m_spectro->setColorMap(colorMap);
        } else {
            QwtLinearColorMap colorMap(Qt::blue, Qt::red);
            colorMap.addColorStop(0.0, Qt::blue);
            colorMap.addColorStop(0.33, Qt::cyan);
            colorMap.addColorStop(0.66, Qt::yellow);
            colorMap.addColorStop(1.0, Qt::red);
            m_spectro->setColorMap(colorMap);
        }
    }
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
                                      m_data(NULL),
                                      m_log10(0)
{
    m_plot = new LWPlot(this);

    QGridLayout *grid = new QGridLayout(this);
    grid->addWidget(m_plot, 0, 0, 1, 1);
    this->setLayout(grid);

    updateLabels();
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
    m_log10 = val;
    ///SetLog10/ChangeRange
    updateGraph();
}

void LWWidget::updateGraph()
{
    if (m_data) {
        m_plot->setData(m_data);
        m_plot->replot();
    }
    updateLabels();
}

void LWWidget::updateLabels()
{
    m_plot->axisWidget(QwtPlot::yRight)->setTitle(m_log10 ? "log Counts" : "Counts");
}
