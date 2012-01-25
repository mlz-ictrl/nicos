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
//
// *****************************************************************************

#ifndef LW_CONTROLS_H
#define LW_CONTROLS_H

#include <QCheckBox>
#include <QLabel>
#include <QLayout>
#include <QMainWindow>
#include <QPushButton>
#include <QSlider>
#include <QSpinBox>

#include "qwt_plot.h"
#include "qwt_plot_curve.h"
#include "qwt_plot_picker.h"

class LWWidget;
class LWControls;

#include "lw_widget.h"
#include "lw_histogram.h"
#include "lw_common.h"


class LWProfileWindow : public QMainWindow
{
    Q_OBJECT

  protected:
    QwtPlot *plot;
    QwtPlotCurve *curve;
    double *data_x, *data_y;

  public:
    LWProfileWindow(QWidget *parent = NULL);
    virtual ~LWProfileWindow();

    void update(LWData *data, double *px, double *py, int width, int bins);
};


class LWControls : public QWidget
{
    Q_OBJECT

    friend class LWWidget;

  private:
    LWWidget *m_widget;
    bool m_sliderupdating;
    double m_absmin, m_absmax, m_absrange;
    double m_curmin, m_curmax, m_currange;

    double m_range_x[2];
    double m_range_y[2];

    double m_histogram_x[256];
    double m_histogram_y[256];

    double m_prof_x[2];
    double m_prof_y[2];

    void showProfWindow(const char *title);

  protected:
    QVBoxLayout *mainLayout;

    QCheckBox *logscaleBox;
    QCheckBox *grayscaleBox;
    QCheckBox *cyclicBox;

    QPushButton *profileButton;
    QSpinBox *profileWidth;
    QLabel *profileWidthLabel;
    QSpinBox *profileBins;
    QLabel *profileBinsLabel;

    QPushButton *xsumButton;
    QPushButton *ysumButton;

    QSlider *minSlider;
    QLabel *minSliderLabel;
    QSlider *maxSlider;
    QLabel *maxSliderLabel;
    QSlider *brtSlider;
    QLabel *brtSliderLabel;
    QSlider *ctrSlider;
    QLabel *ctrSliderLabel;

    QwtPlot *histoPlot;
    LWHistogramItem *histogram;
    QwtPlotCurve *histoRange;
    QwtPlotPicker *histoPicker;

    QwtPlotCurve *profLine1;
    QwtPlotCurve *profLine2;
    LWProfileWindow *profWindow;

    void setupUi();
    void setControls(LWCtrl which);
    void setAxisNames(const char *xaxis, const char *yaxis);

  protected slots:
    void pickRange(const QwtDoubleRect &);
    void updateMinMax();
    void updateBrightness(int);
    void updateContrast(int);
    void setLogscale(bool);
    void setColorMap();
    void dataUpdated(LWData *);
    void pickProfile();
    void createProfile(const QwtArray<QwtDoublePoint> &);
    void updateProfWidth(int);
    void updateProfBins(int);
    void updateProfLineWidth(int);
    void zoomAdjusted();
    void createXSum();
    void createYSum();

  public:
    LWControls(QWidget *parent = NULL);
    virtual ~LWControls();
};

#endif
