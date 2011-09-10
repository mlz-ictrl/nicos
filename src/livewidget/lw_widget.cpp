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
    m_plot = new LWPlot(this);
    setStandardColorMap(false, false);

    m_controls = new LWControls(this);

    QHBoxLayout *layout = new QHBoxLayout(this);
    layout->addWidget(m_plot);
    layout->addWidget(m_controls);
    this->setLayout(layout);
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
    updateGraph(true);
    m_plot->getZoomer()->setZoomBase();
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

void LWWidget::setKeepAspect(bool val)
{
    if (m_plot->getZoomer()) {
        m_plot->getZoomer()->setKeepAspect(val);
    }
}

bool LWWidget::keepAspect() const
{
    if (m_plot->getZoomer()) {
        return m_plot->getZoomer()->keepAspect();
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
