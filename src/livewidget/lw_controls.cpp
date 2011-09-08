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

#include <iostream>

#include "lw_controls.h"
#include "lw_data.h"


LWControls::LWControls(QWidget *parent) : QWidget(parent)
{
    m_widget = qobject_cast<LWWidget *>(parent);
    m_sliderupdating = false;
    m_range_y[0] = 0;
    m_range_y[1] = 0;
    memset(m_histogram_y, 0, sizeof(m_histogram_y));

    setupUi();
}

LWControls::~LWControls()
{
}

void LWControls::setupUi()
{
    QLabel *minLabel, *maxLabel, *brtLabel, *ctrLabel;
    QGridLayout *gridLayout;

    mainLayout = new QVBoxLayout();
    mainLayout->setObjectName("mainLayout");

    /*
      pushButton = new QPushButton(centralwidget);
      pushButton->setObjectName("pushButton");
      mainLayout->addWidget(pushButton);
    */
    logscaleBox = new QCheckBox("logscale", this);
    logscaleBox->setObjectName("logscaleBox");
    mainLayout->addWidget(logscaleBox);

    grayscaleBox = new QCheckBox("grayscale", this);
    grayscaleBox->setObjectName("grayscaleBox");
    mainLayout->addWidget(grayscaleBox);

    cyclicBox = new QCheckBox("cyclic", this);
    cyclicBox->setObjectName("cyclicBox");
    mainLayout->addWidget(cyclicBox);

    histoPlot = new QwtPlot(this);
    histoPlot->setObjectName("histoPlot");
    QSizePolicy plotSizePolicy(QSizePolicy::Minimum, QSizePolicy::Expanding);
    histoPlot->setSizePolicy(plotSizePolicy);
    histoPlot->enableAxis(QwtPlot::yLeft, false);
    QFont newFont(font());
    newFont.setPointSize(newFont.pointSize() * 0.7);
    histoPlot->setAxisFont(QwtPlot::xBottom, newFont);

    histogram = new QwtPlotCurve();
    histogram->setRenderHint(QwtPlotCurve::RenderAntialiased);
    histogram->setData(QwtCPointerData(m_histogram_x,
                                       m_histogram_y, 256));
    histogram->attach(histoPlot);

    histoRange = new QwtPlotCurve();
    histoRange->setPen(QPen(QBrush(QColor(0, 0, 255, 64)),
                            1000, Qt::SolidLine, Qt::FlatCap));
    histoRange->setData(QwtCPointerData(m_range_x, m_range_y, 2));
    histoRange->attach(histoPlot);

    histoPicker = new QwtPlotPicker(
        QwtPlot::xBottom, QwtPlot::yLeft, QwtPicker::RectSelection,
        QwtPicker::RectRubberBand, QwtPicker::AlwaysOff,
        histoPlot->canvas());
    histoPicker->setRubberBandPen(QPen(Qt::red));

    mainLayout->addWidget(histoPlot);

    QSizePolicy labelSizePolicy(QSizePolicy::Fixed, QSizePolicy::Preferred);
    labelSizePolicy.setHorizontalStretch(0);
    labelSizePolicy.setVerticalStretch(0);
    QSizePolicy sliderSizePolicy(QSizePolicy::Fixed, QSizePolicy::Fixed);
    sliderSizePolicy.setHorizontalStretch(0);
    sliderSizePolicy.setVerticalStretch(0);

    gridLayout = new QGridLayout();

    minLabel = new QLabel("minimum", this);
    minLabel->setSizePolicy(labelSizePolicy);
    gridLayout->addWidget(minLabel, 0, 0, 1, 1);

    minSlider = new QSlider(this);
    minSlider->setObjectName("minSlider");
    minSlider->setSizePolicy(sliderSizePolicy);
    minSlider->setMinimumSize(QSize(250, 0));
    minSlider->setMaximum(256);
    minSlider->setOrientation(Qt::Horizontal);
    gridLayout->addWidget(minSlider, 0, 1, 1, 1);

    maxLabel = new QLabel("maximum", this);
    maxLabel->setSizePolicy(labelSizePolicy);
    gridLayout->addWidget(maxLabel, 1, 0, 1, 1);

    maxSlider = new QSlider(this);
    maxSlider->setObjectName("maxSlider");
    maxSlider->setSizePolicy(sliderSizePolicy);
    maxSlider->setMinimumSize(QSize(250, 0));
    maxSlider->setMaximum(256);
    maxSlider->setValue(256);
    maxSlider->setOrientation(Qt::Horizontal);
    gridLayout->addWidget(maxSlider, 1, 1, 1, 1);

    brtLabel = new QLabel("brightness", this);
    brtLabel->setSizePolicy(labelSizePolicy);
    gridLayout->addWidget(brtLabel, 2, 0, 1, 1);

    brtSlider = new QSlider(this);
    brtSlider->setObjectName("brtSlider");
    brtSlider->setSizePolicy(sliderSizePolicy);
    brtSlider->setMinimumSize(QSize(250, 0));
    brtSlider->setMaximum(256);
    brtSlider->setValue(128);
    brtSlider->setOrientation(Qt::Horizontal);
    gridLayout->addWidget(brtSlider, 2, 1, 1, 1);

    ctrLabel = new QLabel("contrast", this);
    ctrLabel->setSizePolicy(labelSizePolicy);
    gridLayout->addWidget(ctrLabel, 3, 0, 1, 1);

    ctrSlider = new QSlider(this);
    ctrSlider->setObjectName("ctrSlider");
    ctrSlider->setSizePolicy(sliderSizePolicy);
    ctrSlider->setMinimumSize(QSize(250, 0));
    ctrSlider->setMaximum(256);
    ctrSlider->setValue(128);
    ctrSlider->setOrientation(Qt::Horizontal);
    gridLayout->addWidget(ctrSlider, 3, 1, 1, 1);

    mainLayout->addLayout(gridLayout);
    setLayout(mainLayout);

    QMetaObject::connectSlotsByName(this);
    QObject::connect(logscaleBox, SIGNAL(toggled(bool)),
                     this, SLOT(setLogscale(bool)));
    QObject::connect(grayscaleBox, SIGNAL(toggled(bool)),
                     this, SLOT(setColorMap()));
    QObject::connect(cyclicBox, SIGNAL(toggled(bool)),
                     this, SLOT(setColorMap()));
    QObject::connect(histoPicker, SIGNAL(selected(const QwtDoubleRect &)),
                     this, SLOT(pickRange(const QwtDoubleRect &)));
    QObject::connect(minSlider, SIGNAL(valueChanged(int)),
                     this, SLOT(updateMinMax()));
    QObject::connect(maxSlider, SIGNAL(valueChanged(int)),
                     this, SLOT(updateMinMax()));
    QObject::connect(brtSlider, SIGNAL(valueChanged(int)),
                     this, SLOT(updateBrightness(int)));
    QObject::connect(ctrSlider, SIGNAL(valueChanged(int)),
                     this, SLOT(updateContrast(int)));
}

void LWControls::updateNewData()
{
    LWData *data = m_widget->data();

    m_absmin = data->min();
    m_absmax = data->max();
    m_absrange = m_absmax - m_absmin;

    m_curmin = m_absmin;
    m_curmax = m_absmax;
    m_currange = m_absrange;

    m_range_x[0] = m_curmin;
    m_range_x[1] = m_curmax;

    data->histogram(256, m_histogram_x, m_histogram_y);
    histoPlot->replot();
}

void LWControls::pickRange(const QwtDoubleRect &rect)
{
    m_sliderupdating = true;
    if (rect.width() == 0) {
        minSlider->setValue(0);
        maxSlider->setValue(256);
    } else {
        minSlider->setValue((rect.left() - m_absmin)/m_absrange * 256);
        maxSlider->setValue((rect.right() - m_absmin)/m_absrange * 256);
    }
    m_sliderupdating = false;
    updateMinMax();
}

void LWControls::updateMinMax()
{
    if (m_sliderupdating)
        return;
    m_curmin = m_absmin + m_absrange * (minSlider->value() / 256.);
    m_curmax = m_absmin + m_absrange * (maxSlider->value() / 256.);
    m_currange = m_curmax - m_curmin;
    m_widget->setCustomRange(m_curmin, m_curmax);

    m_range_x[0] = m_curmin;
    m_range_x[1] = m_curmax;
    histoPlot->replot();

    double brightness = 1.0 - (m_curmin + m_currange/2. - m_absmin)/m_absrange;
    double contrast = m_absrange/m_currange * 0.5;
    if (contrast > 0.5)
        contrast = 1.0 - m_currange/m_absrange * 0.5;
    m_sliderupdating = true;
    brtSlider->setValue(256 * brightness);
    ctrSlider->setValue(256 * contrast);
    m_sliderupdating = false;
}

void LWControls::updateBrightness(int level)
{
    if (m_sliderupdating)
        return;
    double dlevel = level / 256.;
    double center = m_absmin + m_absrange * (1.0 - dlevel);
    double width = m_curmax - m_curmin;
    m_curmin = center - width/2.;
    m_curmax = center + width/2.;
    m_currange = m_curmax - m_curmin;
    m_widget->setCustomRange(m_curmin, m_curmax);

    m_range_x[0] = m_curmin;
    m_range_x[1] = m_curmax;
    histoPlot->replot();

    m_sliderupdating = true;
    minSlider->setValue((m_curmin - m_absmin)/m_absrange * 256);
    maxSlider->setValue((m_curmax - m_absmin)/m_absrange * 256);
    m_sliderupdating = false;
}

void LWControls::updateContrast(int level)
{
    if (m_sliderupdating)
        return;
    double dlevel = level / 256.;
    double center = m_curmin + m_currange/2.;
    double slope;
    if (dlevel <= 0.5)
        slope = dlevel / 0.5;
    else if (dlevel < 1.)
        slope = 0.5 / (1 - dlevel);
    else
        return;
    if (slope > 0) {
        m_curmin = center - (0.5 * m_absrange)/slope;
        m_curmax = center + (0.5 * m_absrange)/slope;
        m_currange = m_curmax - m_curmin;
        m_widget->setCustomRange(m_curmin, m_curmax);

        m_range_x[0] = m_curmin;
        m_range_x[1] = m_curmax;
        histoPlot->replot();

        m_sliderupdating = true;
        minSlider->setValue((m_curmin - m_absmin)/m_absrange * 256);
        maxSlider->setValue((m_curmax - m_absmin)/m_absrange * 256);
        m_sliderupdating = false;
    }
}

void LWControls::setLogscale(bool on)
{
    m_widget->setLog10(on);
    updateNewData();
}

void LWControls::setColorMap()
{
    m_widget->setStandardColorMap(grayscaleBox->isChecked(),
                                  cyclicBox->isChecked());
}
