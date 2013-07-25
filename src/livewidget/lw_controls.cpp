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
//   Georg Brandl <georg.brandl@frm2.tum.de>
//   Philipp Schmakat <philipp.schmakat@frm2.tum.de>
//
// *****************************************************************************

#include <iostream>
#include <stdio.h>

#include "lw_controls.h"
#include "lw_widget.h"
#include "lw_imageproc.h"


LWControls::LWControls(QWidget *parent) : QWidget(parent)
{
    m_widget = qobject_cast<LWWidget *>(parent);
    m_sliderupdating = false;
    m_range_y[0] = m_range_y[1] = 0;
    memset(m_histogram_y, 0, sizeof(m_histogram_y));

    profLine0 = profLine1 = profLine2 = 0;
    profWindow = 0;
    m_prof_x[0] = m_prof_x[1] = m_prof_y[0] = m_prof_y[1] = 0;

    setupUi();
}

LWControls::~LWControls()
{
}

void LWControls::setupUi()
{
    QGridLayout *gridLayout;
    QHBoxLayout *hLayout;

    mainLayout = new QVBoxLayout();

    gridBox = new QCheckBox("show grid", this);
    mainLayout->addWidget(gridBox);

    logscaleBox = new QCheckBox("logscale", this);
    mainLayout->addWidget(logscaleBox);

    grayscaleBox = new QCheckBox("grayscale", this);
    mainLayout->addWidget(grayscaleBox);

    cyclicBox = new QCheckBox("cyclic colormap", this);
    mainLayout->addWidget(cyclicBox);

    // ANTARES/imaging specific controls

    darkfieldBox = new QCheckBox("subtract darkfield image", this);
    mainLayout->addWidget(darkfieldBox);

    normalizeBox = new QCheckBox("normalize to openbeam image", this);
    mainLayout->addWidget(normalizeBox);

    despeckleBox = new QCheckBox("remove gamma spots", this);
    mainLayout->addWidget(despeckleBox);

    hLayout = new QHBoxLayout();
    despeckleValueLabel = new QLabel("despeckle value:", this);
    hLayout->addWidget(despeckleValueLabel);
    despeckleValue = new QSpinBox(this);
    despeckleValue->setRange(1, 65536);
    despeckleValue->setEnabled(false);
    despeckleValue->setValue(3000);
    hLayout->addWidget(despeckleValue);
    mainLayout->addLayout(hLayout);

    operationSelector = new QComboBox();
    operationSelector->addItem("no operation selected");
    operationSelector->addItem("normalize to openbeam image");
    operationSelector->addItem("subtract darkimage");
    operationSelector->addItem("stack average");
    mainLayout->addWidget(operationSelector);

    filterSelector = new QComboBox();
    filterSelector->addItem("no filter selected");
    filterSelector->addItem("3x3 standard median filter");
    filterSelector->addItem("3x3 hybrid median filter");
    filterSelector->addItem("3x3 despeckle filter");
    mainLayout->addWidget(filterSelector);

    // end of imaging specific controls

    hLayout = new QHBoxLayout();
    profileButton = new QPushButton("plot line profile", this);
    profileButton->setCheckable(true);
    hLayout->addWidget(profileButton);
    profileHideButton = new QPushButton("hide profile line", this);
    profileHideButton->setEnabled(false);
    hLayout->addWidget(profileHideButton);
    mainLayout->addLayout(hLayout);

    // prepare a few lines to put on the widget for displaying the
    // current profile line

    profLine0 = new QwtPlotCurve();
    profLine0->setRenderHint(QwtPlotCurve::RenderAntialiased);
    profLine0->setPen(QPen(QBrush(QColor(255, 255, 255, 255)), 3,
                           Qt::SolidLine, Qt::FlatCap));
    profLine0->setData(QwtCPointerData(m_prof_x, m_prof_y, 2));
    profLine0->setVisible(false);
    profLine0->attach(m_widget->plot());

    profLine1 = new QwtPlotCurve();
    profLine1->setRenderHint(QwtPlotCurve::RenderAntialiased);
    profLine1->setPen(QPen(QBrush(QColor(0, 255, 0, 255)), 3,
                           Qt::SolidLine, Qt::FlatCap));
    profLine1->setData(QwtCPointerData(m_prof_x, m_prof_y, 2));
    profLine1->setVisible(false);
    profLine1->attach(m_widget->plot());

    profLine2 = new QwtPlotCurve();
    profLine2->setRenderHint(QwtPlotCurve::RenderAntialiased);
    profLine2->setPen(QPen(QBrush(QColor(0, 255, 0, 96)), 1,
                           Qt::SolidLine, Qt::FlatCap));
    profLine2->setData(QwtCPointerData(m_prof_x, m_prof_y, 2));
    profLine2->setVisible(false);
    profLine2->attach(m_widget->plot());

    hLayout = new QHBoxLayout();
    profileWidthLabel = new QLabel("profile width:", this);
    hLayout->addWidget(profileWidthLabel);
    profileWidth = new QSpinBox(this);
    profileWidth->setRange(1, 65536);
    profileWidth->setEnabled(false);
    hLayout->addWidget(profileWidth);
    mainLayout->addLayout(hLayout);

    hLayout = new QHBoxLayout();
    profileBinsLabel = new QLabel("profile binning:", this);
    hLayout->addWidget(profileBinsLabel);
    profileBins = new QSpinBox(this);
    profileBins->setRange(1, 256);
    profileBins->setEnabled(false);
    hLayout->addWidget(profileBins);
    mainLayout->addLayout(hLayout);

    xsumButton = new QPushButton("integrate over x", this);
    mainLayout->addWidget(xsumButton);
    ysumButton = new QPushButton("integrate over y", this);
    mainLayout->addWidget(ysumButton);


    histoPlot = new QwtPlot(this);
    QSizePolicy plotSizePolicy(QSizePolicy::Minimum, QSizePolicy::Expanding);
    histoPlot->setSizePolicy(plotSizePolicy);
    QFont newSmallFont(font());
    QFont newLargeFont(font());
    newLargeFont.setPointSize(font().pointSize() * 0.8);
    newSmallFont.setPointSize(font().pointSize() * 0.8);
    QwtText title;
    title.setFont(newLargeFont);
    title.setText("histogram", QwtText::AutoText);
    histoPlot->setTitle(title);
    histoPlot->enableAxis(QwtPlot::yLeft, false);
    histoPlot->setFixedHeight(180);
    histoPlot->setAxisFont(QwtPlot::xBottom, newSmallFont);

    histogram = new LWHistogramItem();
    //histogram->setRenderHint(QwtPlotCurve::RenderAntialiased);
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
    QSizePolicy sliderSizePolicy(QSizePolicy::Expanding, QSizePolicy::Fixed);
    sliderSizePolicy.setHorizontalStretch(0);
    sliderSizePolicy.setVerticalStretch(0);
    QSizePolicy vSpacerPolicy(QSizePolicy::Fixed, QSizePolicy::Expanding);
    vSpacerPolicy.setHorizontalStretch(0);
    vSpacerPolicy.setVerticalStretch(0);

    gridLayout = new QGridLayout();

    minSliderLabel = new QLabel("minimum", this);
    minSliderLabel->setSizePolicy(labelSizePolicy);
    gridLayout->addWidget(minSliderLabel, 0, 0, 1, 1);

    minSlider = new QSlider(this);
    minSlider->setSizePolicy(sliderSizePolicy);
    minSlider->setMinimumSize(QSize(250, 0));
    minSlider->setMaximum(256);
    minSlider->setOrientation(Qt::Horizontal);
    gridLayout->addWidget(minSlider, 0, 1, 1, 1);

    maxSliderLabel = new QLabel("maximum", this);
    maxSliderLabel->setSizePolicy(labelSizePolicy);
    gridLayout->addWidget(maxSliderLabel, 1, 0, 1, 1);

    maxSlider = new QSlider(this);
    maxSlider->setSizePolicy(sliderSizePolicy);
    maxSlider->setMinimumSize(QSize(250, 0));
    maxSlider->setMaximum(256);
    maxSlider->setValue(256);
    maxSlider->setOrientation(Qt::Horizontal);
    gridLayout->addWidget(maxSlider, 1, 1, 1, 1);

    brtSliderLabel = new QLabel("brightness", this);
    brtSliderLabel->setSizePolicy(labelSizePolicy);
    gridLayout->addWidget(brtSliderLabel, 2, 0, 1, 1);

    brtSlider = new QSlider(this);
    brtSlider->setSizePolicy(sliderSizePolicy);
    brtSlider->setMinimumSize(QSize(250, 0));
    brtSlider->setMaximum(256);
    brtSlider->setValue(128);
    brtSlider->setOrientation(Qt::Horizontal);
    gridLayout->addWidget(brtSlider, 2, 1, 1, 1);

    ctrSliderLabel = new QLabel("contrast", this);
    ctrSliderLabel->setSizePolicy(labelSizePolicy);
    gridLayout->addWidget(ctrSliderLabel, 3, 0, 1, 1);

    ctrSlider = new QSlider(this);
    ctrSlider->setSizePolicy(sliderSizePolicy);
    ctrSlider->setMinimumSize(QSize(250, 0));
    ctrSlider->setMaximum(256);
    ctrSlider->setValue(128);
    ctrSlider->setOrientation(Qt::Horizontal);
    gridLayout->addWidget(ctrSlider, 3, 1, 1, 1);

    mainLayout->addLayout(gridLayout);

    // list of "previous" files -- this needs to be cleaned up

    filelistLabel = new QLabel("directory", this);
    mainLayout->addWidget(filelistLabel);

    filelistDirectory = new QLineEdit(".", this);
    mainLayout->addWidget(filelistDirectory);

    filelistView = new QListView(this);
    filelistModel = new QStandardItemModel(this);
    filelistItem = new QStandardItem();

    filelistView->setModel(filelistModel);
    mainLayout->addWidget(filelistView);

    listFiles();

    mainLayout->addStretch();
    setLayout(mainLayout);

    QMetaObject::connectSlotsByName(this);
    QObject::connect(gridBox, SIGNAL(toggled(bool)),
                     this, SLOT(setGrid(bool)));
    QObject::connect(logscaleBox, SIGNAL(toggled(bool)),
                     this, SLOT(setLogscale(bool)));
    QObject::connect(grayscaleBox, SIGNAL(toggled(bool)),
                     this, SLOT(setColorMap()));
    QObject::connect(cyclicBox, SIGNAL(toggled(bool)),
                     this, SLOT(setColorMap()));
    QObject::connect(normalizeBox, SIGNAL(toggled(bool)),
                     this, SLOT(setNormalize(bool)));
    QObject::connect(darkfieldBox, SIGNAL(toggled(bool)),
                     this, SLOT(setDarkfieldSubtract(bool)));
    QObject::connect(despeckleBox, SIGNAL(toggled(bool)),
                     this, SLOT(setDespeckle(bool)));
    QObject::connect(despeckleValue, SIGNAL(valueChanged(int)),
                     this, SLOT(updateDespeckleValue(int)));
    QObject::connect(operationSelector, SIGNAL(activated(int)),
                     this, SLOT(updateOperationSelector(int)));
    QObject::connect(filterSelector, SIGNAL(activated(int)),
                     this, SLOT(updateFilterSelector(int)));
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
    QObject::connect(profileHideButton, SIGNAL(released()),
                     this, SLOT(hideProfileLine()));
    QObject::connect(profileWidth, SIGNAL(valueChanged(int)),
                     this, SLOT(updateProfWidth(int)));
    QObject::connect(profileBins, SIGNAL(valueChanged(int)),
                     this, SLOT(updateProfBins(int)));
    QObject::connect(xsumButton, SIGNAL(released()),
                     this, SLOT(createXSum()));
    QObject::connect(ysumButton, SIGNAL(released()),
                     this, SLOT(createYSum()));
    QObject::connect(m_widget->plot()->getPicker(),
                     SIGNAL(selected(const QwtArray<QwtDoublePoint> &)), this,
                     SLOT(createProfile(const QwtArray<QwtDoublePoint> &)));
    QObject::connect(m_widget->plot()->getZoomer(),
                     SIGNAL(zoomed(const QwtDoubleRect &)), this,
                     SLOT(zoomAdjusted()));
    QObject::connect(filelistDirectory, SIGNAL(returnPressed()),
                     this, SLOT(listFiles()));
    QObject::connect(filelistView, SIGNAL(clicked(QModelIndex)),
                     this, SLOT(selectFile(QModelIndex)));
}

void LWControls::dataUpdated(LWData *data)
{
    m_absmin = data->min();
    m_absmax = data->max();
    if (data->hasCustomRange()) {
        m_curmin = data->customRangeMin();
        m_curmax = data->customRangeMax();
    } else {
        m_curmin = m_absmin;
        m_curmax = m_absmax;
    }
    m_absrange = m_currange = m_absmax - m_absmin;

    m_range_x[0] = m_curmin;
    m_range_x[1] = m_curmax;

    data->histogram(256, m_histogram_x, m_histogram_y);
    histoPlot->replot();

    m_sliderupdating = true;
    minSlider->setValue((m_curmin - m_absmin)/m_absrange * 256);
    maxSlider->setValue((m_curmax - m_absmin)/m_absrange * 256);
    double brightness = 1.0 - (m_curmin + m_currange/2. - m_absmin)/m_absrange;
    double contrast = m_absrange/m_currange * 0.5;
    if (contrast > 0.5)
        contrast = 1.0 - m_currange/m_absrange * 0.5;
    brtSlider->setValue(256 * brightness);
    ctrSlider->setValue(256 * contrast);
    m_sliderupdating = false;

    if (profWindow)
        profWindow->update(m_widget->data(), m_prof_x, m_prof_y,
                           profileWidth->value(), profileBins->value(),
                           m_prof_type);
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

void LWControls::setGrid(bool on)
{
    m_widget->setGrid(on);
}

void LWControls::setLogscale(bool on)
{
    m_widget->setLog10(on);
}

void LWControls::setNormalize(bool on)
{
    m_widget->setNormalized(on);
}

void LWControls::setDarkfieldSubtract(bool on)
{
    m_widget->setDarkfieldSubtracted(on);
}

void LWControls::setDespeckle(bool on)
{
    m_widget->setDespeckled(on);
    despeckleValue->setEnabled(on);
}

void LWControls::setColorMap()
{
    m_widget->setStandardColorMap(grayscaleBox->isChecked(),
                                  cyclicBox->isChecked());
}

void LWControls::pickProfile()
{
    if (!m_widget->data())
        return;
    m_widget->plot()->getPicker()->setEnabled(true);
    m_widget->plot()->getZoomer()->setEnabled(false);
    profileButton->setText("click two points on image");
    profileButton->setChecked(true);
}

void LWControls::showProfWindow(const char *title)
{
    if (profWindow == NULL)
        profWindow = new LWProfileWindow(this, m_widget);
    profWindow->update(m_widget->data(), m_prof_x, m_prof_y,
                       profileWidth->value(), profileBins->value(),
                       m_prof_type);
    profWindow->setWindowTitle(title);
    if (!m_widget->instrument() == INSTR_TOFTOF) {
        profWindow->show();
        profileHideButton->setEnabled(true);
        profileWidth->setEnabled(true);
        profileBins->setEnabled(true);
    }
}

void LWControls::createProfile(const QwtArray<QwtDoublePoint> &points)
{
    m_widget->plot()->getPicker()->setEnabled(false);
    m_widget->plot()->getZoomer()->setEnabled(true);
    profileButton->setText("plot line profile");
    profileButton->setChecked(false);
    if (points.size() != 2)
        return;
    m_prof_x[0] = points[0].x();
    m_prof_y[0] = points[0].y();
    m_prof_x[1] = points[1].x();
    m_prof_y[1] = points[1].y();
    m_prof_type = 2;

    profLine0->setVisible(true);
    profLine1->setVisible(true);
    profLine2->setVisible(true);
    updateProfLineWidth(profileWidth->value());  // does replot

    showProfWindow("Line profile");
}

void LWControls::hideProfileLine()
{
    profLine0->setVisible(false);
    profLine1->setVisible(false);
    profLine2->setVisible(false);
    profWindow->close();
    profileHideButton->setEnabled(false);
    profileWidth->setEnabled(false);
    profileBins->setEnabled(false);
    m_widget->plot()->replot();
}


void LWControls::createYSum()
{
    if (!m_widget->data())
        return;
    m_prof_type = 1;
    m_prof_x[0] = 0;
    m_prof_x[1] = m_widget->data()->width();
    m_prof_y[0] = m_widget->data()->height() / 2;
    m_prof_y[1] = m_widget->data()->height() / 2;
    profileWidth->setValue(m_widget->data()->height());
    showProfWindow("Y Integration");
}

void LWControls::createXSum()
{
    if (!m_widget->data())
        return;
    m_prof_type = 0;
    m_prof_y[0] = 0;
    m_prof_y[1] = m_widget->data()->height();
    m_prof_x[0] = m_widget->data()->width() / 2;
    m_prof_x[1] = m_widget->data()->width() / 2;
    profileWidth->setValue(m_widget->data()->width());
    showProfWindow("X Integration");
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
    if (profWindow)
        profWindow->update(m_widget->data(), m_prof_x, m_prof_y, w,
                           profileBins->value(), m_prof_type);
}

void LWControls::updateProfBins(int b)
{
    if (profWindow)
        profWindow->update(m_widget->data(), m_prof_x, m_prof_y,
                           profileWidth->value(), b, m_prof_type);
}


void LWControls::updateOperationSelector(int comboBoxValue)
{
    if (m_widget->isImageOperation() != LWImageOperations(comboBoxValue))
        m_widget->setImageOperation(LWImageOperations(comboBoxValue));
}


void LWControls::updateFilterSelector(int comboBoxValue)
{
    if (m_widget->isImageFilter() != LWImageFilters(comboBoxValue))
        m_widget->setImageFilter(LWImageFilters(comboBoxValue));

    despeckleValue->setEnabled(comboBoxValue == DespeckleFilter);
}


void LWControls::updateDespeckleValue(int value)
{
    m_widget->setDespeckleValue(value);
}


void LWControls::setControls(LWCtrl which)
{
    gridBox->setVisible(which & ShowGrid);
    logscaleBox->setVisible(which & Logscale);
    grayscaleBox->setVisible(which & Grayscale);
    cyclicBox->setVisible(which & Cyclic);

    darkfieldBox->setVisible(which & Darkfield);
    normalizeBox->setVisible(which & Normalize);
    despeckleBox->setVisible(which & Despeckle);
    despeckleValueLabel->setVisible(which & Despeckle);
    despeckleValue->setVisible(which & Despeckle);

    filterSelector->setVisible(which & ImageOperations);
    operationSelector->setVisible(which & ImageOperations);

    profileButton->setVisible(which & CreateProfile);
    profileHideButton->setVisible(which & CreateProfile);
    profileWidth->setVisible(which & CreateProfile);
    profileBins->setVisible(which & CreateProfile);
    profileWidthLabel->setVisible(which & CreateProfile);
    profileBinsLabel->setVisible(which & CreateProfile);

    xsumButton->setVisible(which & Integrate);
    ysumButton->setVisible(which & Integrate);

    histoPlot->setVisible(which & Histogram);

    minSlider->setVisible(which & MinimumMaximum);
    maxSlider->setVisible(which & MinimumMaximum);
    minSliderLabel->setVisible(which & MinimumMaximum);
    maxSliderLabel->setVisible(which & MinimumMaximum);
    brtSlider->setVisible(which & BrightnessContrast);
    ctrSlider->setVisible(which & BrightnessContrast);
    brtSliderLabel->setVisible(which & BrightnessContrast);
    ctrSliderLabel->setVisible(which & BrightnessContrast);

    filelistLabel->setVisible(which & Filelist);
    filelistDirectory->setVisible(which & Filelist);
    filelistView->setVisible(which & Filelist);
}

void LWControls::setAxisNames(const char *xaxis, const char *yaxis)
{
    QString tmp1("integrate over ");
    QString tmp2("integrate over ");
    tmp1 += xaxis;
    tmp2 += yaxis;
    xsumButton->setText(tmp1);
    ysumButton->setText(tmp2);
}


void LWControls::listFiles()
{
    filelistModel->clear();

    QString location = filelistDirectory->text();
    QDir dir(location);

    if (dir.exists()) {
        QFileInfoList entries = dir.entryInfoList(QDir::NoDotAndDotDot | QDir::Files);
        foreach (QFileInfo entryInfo, entries) {
            QString path = entryInfo.absoluteFilePath();
            filelistItem->setText(path);
            filelistModel->appendRow(filelistItem->clone());
        }
    }
}

void LWControls::selectFile(QModelIndex index)
{
    QString filename = filelistModel->itemFromIndex(index)->text();
    QByteArray char_array = filename.toLatin1();
    const char *pFilename = char_array.data();

    LWData *data;
    data = new LWData(pFilename, TYPE_FITS);
    m_widget->setData(data);
}
