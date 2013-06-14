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
//
// *****************************************************************************

#include <iostream>

#include <QLayout>

#include "lw_widget.h"

/** LWWidget ******************************************************************/

LWWidget::LWWidget(QWidget *parent) : QWidget(parent), m_data(NULL)
{
    m_instr = INSTR_NONE;

    m_plot = new LWPlot(this);
    m_plot->setSizePolicy(QSizePolicy::Minimum, QSizePolicy::MinimumExpanding);

    setStandardColorMap(false, false);

    m_controls = new LWControls(this);
    m_controls->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::MinimumExpanding);

    QFrame *verticalLine = new QFrame(this);
    verticalLine->setFrameStyle(QFrame::VLine);
    verticalLine->setSizePolicy(QSizePolicy::Minimum,QSizePolicy::Expanding);

    QHBoxLayout *layout = new QHBoxLayout(this);
    layout->addWidget(m_plot, 0, Qt::AlignLeft);
    layout->addWidget(verticalLine);
    layout->addWidget(m_controls);
    this->setLayout(layout);
}

LWWidget::~LWWidget()
{
    unload();
}

void LWWidget::setInstrumentOption(const char *instr)
{
    if (strcmp(instr, "toftof") == 0)
        m_instr = INSTR_TOFTOF;
    else if (strcmp(instr, "antares") == 0)
        m_instr = INSTR_IMAGING;
    else
        m_instr = INSTR_NONE;
}

void LWWidget::unload()
{
    // XXX why was this removed?
    /*
    if (m_data) {
        delete m_data;
        m_data = NULL;
    }
    */
}

void LWWidget::resizeEvent(QResizeEvent *event)
{
    if (isKeepAspect()) {
        // approximate the width of the axes and colorbar and keep
        // widget square shaped
        m_plot->setFixedWidth(m_plot->height() + 140);
    }

    QWidget::resizeEvent(event);
}

void LWWidget::setData(LWData *data)
{
    bool prev_log10 = false;
    /*
    bool prev_despeckled = false;
    bool prev_darkimagesubtracted = false;
    bool prev_normalized = false;
    */

    double prev_min = -1, prev_max = -1;
    if (m_data) {
        prev_log10 = m_data->isLog10();
        if (m_data->hasCustomRange()) {
            prev_min = m_data->customRangeMin();
            prev_max = m_data->customRangeMax();
        }
        unload();
    }

    // apply image operations here
    // ...
    m_data = data;

    m_data->setLog10(prev_log10);
    if (prev_min != -1 || prev_max != -1)
        m_data->setCustomRange(prev_min, prev_max);

    updateGraph(true);
    if (m_plot->getZoomer()->zoomRectIndex() == 0) {
        // re-set zoom base only if not zoomed
        m_plot->getZoomer()->setZoomBase();
    }
}

void LWWidget::setGrid(bool val)
{
    if (m_showgrid != val) {
        if (m_plot) {
            m_plot->setGrid(val);
            m_showgrid = val;
            updateGraph(true);
        }
    }
}

bool LWWidget::hasGrid() const
{
    if (m_plot) {
        return m_plot->hasGrid();
    }
    return false;
}

void LWWidget::setLog10(bool val)
{
    if (m_data) {
        m_data->setLog10(val);
        updateGraph(true);
    }
}

bool LWWidget::isLog10() const
{
    if (m_data) {
        return m_data->isLog10();
    }
    return false;
}

void LWWidget::setNormalized(bool val)
{
    if (m_data) {
        m_data->setNormalized(val);
        updateGraph(true);
    }
}

bool LWWidget::isNormalized() const
{
    if (m_data) {
        return m_data->isNormalized();
    }
    return false;
}

void LWWidget::setDarkfieldSubtracted(bool val)
{
    if (m_data) {
        m_data->setDarkfieldSubtracted(val);
        updateGraph(true);
    }
}

bool LWWidget::isDarkfieldSubtracted() const
{
    if (m_data) {
        return m_data->isDarkfieldSubtracted();
    }
    return false;
}

void LWWidget::setDespeckled(bool val)
{
    if (m_data) {
        m_data->setDespeckled(val);
        updateGraph(true);
    }
}

bool LWWidget::isDespeckled() const
{
    if (m_data) {
        return m_data->isDespeckled();
    }
    return false;
}

void LWWidget::setDespeckleValue(float value)
{
    if (m_data) {
        m_data->setDespeckleValue(value);
        updateGraph(true);
    }
}

void LWWidget::setImageFilter(LWImageFilters which)
{
    if (m_data) {
        m_data->setImageFilter(which);
        updateGraph(true);
    }
}



LWImageFilters LWWidget::isImageFilter() const
{
    if (m_data) {
        return m_data->isImageFilter();
    }
    return NoImageFilter;
}


void LWWidget::setImageOperation(LWImageOperations which)
{
    if (m_data) {
        m_data->setImageOperation(which);
        updateGraph(true);
    }
}

LWImageOperations LWWidget::isImageOperation() const
{
    if (m_data) {
        return m_data->isImageOperation();
    }
    return NoImageOperation;
}


void LWWidget::setKeepAspect(bool val)
{
    if (m_plot->getZoomer()) {
        m_plot->getZoomer()->setKeepAspect(val);
    }
}

bool LWWidget::isKeepAspect() const
{
    if (m_plot->getZoomer()) {
        return m_plot->getZoomer()->isKeepAspect();
    }
    return false;
}

void LWWidget::setControlsVisible(bool val)
{
    m_controls->setVisible(val);
}

bool LWWidget::controlsVisible() const
{
    return m_controls->isVisible();
}

void LWWidget::setStandardColorMap(bool greyscale, bool cyclic)
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
    updateGraph(false);
}

void LWWidget::setAxisLabels(const char *xaxis, const char *yaxis)
{
    m_plot->axisWidget(QwtPlot::xBottom)->setTitle(xaxis);
    m_plot->axisWidget(QwtPlot::yLeft)->setTitle(yaxis);
    m_controls->setAxisNames(xaxis, yaxis);
}

void LWWidget::setCustomRange(double lower, double upper)
{
    if (m_data) {
        m_data->setCustomRange(lower, upper);
        updateGraph(false);
    }
}

void LWWidget::updateGraph(bool newdata)
{
    if (m_data) {
        m_plot->setData(new LWRasterData(m_data));

        updateLabels();
        if (newdata)
            emit dataUpdated(m_data);
    }
}

void LWWidget::updateLabels()
{
    if (m_data)
        m_plot->axisWidget(QwtPlot::yRight)->setTitle(
            m_data->isLog10() ? "log Counts" : "Counts");
}

void LWWidget::hideProfileLine()
{
    m_controls->hideProfileLine();
}

void LWWidget::setControls(LWCtrl which)
{
    m_controls->setControls(which);
}

int LWWidget::instrument()
{
    return m_instr;
}
