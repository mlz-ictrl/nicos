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
    m_range_y[0] = m_range_y[1] = 0;
    memset(m_histogram_y, 0, sizeof(m_histogram_y));

    profLine1 = 0;
    profLine2 = 0;
    profWindow = 0;
    m_prof_x[0] = m_prof_x[1] = m_prof_y[0] = m_prof_y[1] = 0;

    setupUi();
}

LWControls::~LWControls()
{
}

void LWControls::setupUi()
{
    QLabel *wLabel, *minLabel, *maxLabel, *brtLabel, *ctrLabel;
    QGridLayout *gridLayout;
    QHBoxLayout *hLayout;

    mainLayout = new QVBoxLayout();

    logscaleBox = new QCheckBox("logscale", this);
    mainLayout->addWidget(logscaleBox);

    grayscaleBox = new QCheckBox("grayscale", this);
    mainLayout->addWidget(grayscaleBox);

    cyclicBox = new QCheckBox("cyclic", this);
    mainLayout->addWidget(cyclicBox);

    profileButton = new QPushButton("create profile", this);
    profileButton->setCheckable(true);
    mainLayout->addWidget(profileButton);

    profLine1 = new QwtPlotCurve();
    profLine1->setRenderHint(QwtPlotCurve::RenderAntialiased);
    profLine1->setPen(QPen(QBrush(QColor(0, 0, 255, 255)), 1,
                           Qt::SolidLine, Qt::FlatCap));
    profLine1->setData(QwtCPointerData(m_prof_x, m_prof_y, 2));
    profLine1->setVisible(false);
    profLine1->attach(m_widget->plot());

    profLine2 = new QwtPlotCurve();
    profLine2->setRenderHint(QwtPlotCurve::RenderAntialiased);
    profLine2->setPen(QPen(QBrush(QColor(0, 0, 255, 96)), 1,
                           Qt::SolidLine, Qt::FlatCap));
    profLine2->setData(QwtCPointerData(m_prof_x, m_prof_y, 2));
    profLine2->setVisible(false);
    profLine2->attach(m_widget->plot());

    hLayout = new QHBoxLayout();
    wLabel = new QLabel("profile width:", this);
    hLayout->addWidget(wLabel);
    profileWidth = new QSpinBox(this);
    profileWidth->setRange(1, 65536);
    hLayout->addWidget(profileWidth);
    mainLayout->addLayout(hLayout);

    hLayout = new QHBoxLayout();
    wLabel = new QLabel("profile binning:", this);
    hLayout->addWidget(wLabel);
    profileBins = new QSpinBox(this);
    profileBins->setRange(1, 256);
    hLayout->addWidget(profileBins);
    mainLayout->addLayout(hLayout);

    histoPlot = new QwtPlot(this);
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
    minSlider->setSizePolicy(sliderSizePolicy);
    minSlider->setMinimumSize(QSize(250, 0));
    minSlider->setMaximum(256);
    minSlider->setOrientation(Qt::Horizontal);
    gridLayout->addWidget(minSlider, 0, 1, 1, 1);

    maxLabel = new QLabel("maximum", this);
    maxLabel->setSizePolicy(labelSizePolicy);
    gridLayout->addWidget(maxLabel, 1, 0, 1, 1);

    maxSlider = new QSlider(this);
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
    QObject::connect(m_widget, SIGNAL(dataUpdated(LWData *)),
                     this, SLOT(dataUpdated(LWData *)));
    QObject::connect(profileButton, SIGNAL(released()),
                     this, SLOT(pickProfile()));
    QObject::connect(profileWidth, SIGNAL(valueChanged(int)),
                     this, SLOT(updateProfWidth(int)));
    QObject::connect(profileBins, SIGNAL(valueChanged(int)),
                     this, SLOT(updateProfBins(int)));
    QObject::connect(m_widget->plot()->getPicker(),
                     SIGNAL(selected(const QwtArray<QwtDoublePoint> &)), this,
                     SLOT(createProfile(const QwtArray<QwtDoublePoint> &)));
    QObject::connect(m_widget->plot()->getZoomer(),
                     SIGNAL(zoomed(const QwtDoubleRect &)), this,
                     SLOT(zoomAdjusted()));
}

void LWControls::dataUpdated(LWData *data)
{
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

    m_sliderupdating = true;
    minSlider->setValue(0);
    maxSlider->setValue(256);
    brtSlider->setValue(128);
    ctrSlider->setValue(128);
    m_sliderupdating = false;

    if (profWindow) {
        profWindow->update(m_widget->data(), m_prof_x, m_prof_y,
                           profileWidth->value(), profileBins->value());
    }
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
}

void LWControls::setColorMap()
{
    m_widget->setStandardColorMap(grayscaleBox->isChecked(),
                                  cyclicBox->isChecked());
}

void LWControls::pickProfile()
{
    m_widget->plot()->getPicker()->setEnabled(true);
    m_widget->plot()->getZoomer()->setEnabled(false);
    profileButton->setText("click two points on image");
    profileButton->setChecked(true);
}

void LWControls::createProfile(const QwtArray<QwtDoublePoint> &points)
{
    m_widget->plot()->getPicker()->setEnabled(false);
    m_widget->plot()->getZoomer()->setEnabled(true);
    profileButton->setText("create profile");
    profileButton->setChecked(false);
    if (points.size() != 2)
        return;
    m_prof_x[0] = points[0].x();
    m_prof_y[0] = points[0].y();
    m_prof_x[1] = points[1].x();
    m_prof_y[1] = points[1].y();

    profLine1->setVisible(true);
    profLine2->setVisible(true);
    updateProfLineWidth(profileWidth->value());  // does replot

    if (profWindow == NULL) {
        profWindow = new LWProfileWindow(this);
    }
    profWindow->update(m_widget->data(), m_prof_x, m_prof_y,
                       profileWidth->value(), profileBins->value());
    profWindow->show();
}

void LWControls::zoomAdjusted()
{
    updateProfLineWidth(profileWidth->value());
}

void LWControls::updateProfLineWidth(int w)
{
    double scale_x = m_widget->plot()->canvasMap(QwtPlot::xBottom).pDist() /
        m_widget->plot()->canvasMap(QwtPlot::xBottom).sDist();
    double scale_y = m_widget->plot()->canvasMap(QwtPlot::yLeft).pDist() /
        m_widget->plot()->canvasMap(QwtPlot::yLeft).sDist();
    double alpha = atan2(m_prof_y[1] - m_prof_y[0], m_prof_x[1] - m_prof_x[0]);
    double width = w * (scale_y * pow(cos(alpha), 2) +
                        scale_x * pow(sin(alpha), 2));
    profLine2->setPen(QPen(QBrush(QColor(0, 0, 255, 96)), width,
                           Qt::SolidLine, Qt::FlatCap));
    m_widget->plot()->replot();
}

void LWControls::updateProfWidth(int w)
{
    updateProfLineWidth(w);
    if (profWindow) {
        profWindow->update(m_widget->data(), m_prof_x, m_prof_y, w,
                           profileBins->value());
    }
}

void LWControls::updateProfBins(int b)
{
    if (profWindow) {
        profWindow->update(m_widget->data(), m_prof_x, m_prof_y,
                           profileWidth->value(), b);
    }
}


/** LWProfileWindow ***********************************************************/

LWProfileWindow::LWProfileWindow(QWidget *parent) :
    QMainWindow(parent), data_x(0), data_y(0)
{
    plot = new QwtPlot(this);
    curve = new QwtPlotCurve();
    curve->setRenderHint(QwtPlotCurve::RenderAntialiased);
    curve->attach(plot);
    setCentralWidget(plot);
    setWindowTitle("Line profile");
    setContentsMargins(5, 5, 5, 5);
    QFont plotfont(font());
    plotfont.setPointSize(plotfont.pointSize() * 0.7);
    plot->setAxisFont(QwtPlot::xBottom, plotfont);
    plot->setAxisFont(QwtPlot::yLeft, plotfont);
    plot->setCanvasBackground(Qt::white);
    resize(800, 200);
}

LWProfileWindow::~LWProfileWindow()
{
}

void LWProfileWindow::update(LWData *data, double *px, double *py, int w, int b)
{
    int start, end, nbins, direction;
    if (data_x) {
        delete[] data_x;
        data_x = 0;
        delete[] data_y;
        data_y = 0;
    }
    if ((int)px[0] == (int)px[1]) {
        start = (int)py[0];
        end = (int)py[1];
        nbins = (abs(end - start) + 1) / b;
        direction = start < end ? 1 : -1;
        data_x = new double[nbins];
        data_y = new double[nbins];
        for (int i = 0; i < nbins; i++) {
            data_x[i] = start + i*direction;
            data_y[i] = 0;
            for (int j = -w+1; j <= w-1; j++)
                for (int k = 0; k < b; k++)
                    data_y[i] += data->value((int)px[0] + j, start + (i*b+k)*direction);
        }
    } else if ((int)py[0] == (int)py[1]) {
        start = (int)px[0];
        end = (int)px[1];
        nbins = (abs(end - start) + 1) / b;
        direction = start < end ? 1 : -1;
        data_x = new double[nbins];
        data_y = new double[nbins];
        for (int i = 0; i < nbins; i++) {
            data_x[i] = start + i*direction;
            data_y[i] = 0;
            for (int j = -w+1; j <= w-1; j++)
                for (int k = 0; k < b; k++)
                    data_y[i] += data->value(start+(i*b+k)*direction, (int)py[0] + j);
        }
    } else {
        curve->setData(QwtCPointerData(data_x, data_y, 0));
        return;
    }
    curve->setData(QwtCPointerData(data_x, data_y, nbins));
    plot->replot();
}
