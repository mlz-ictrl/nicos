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

#ifndef LW_CONTROLS_H
#define LW_CONTROLS_H

#include <QCheckBox>
#include <QLabel>
#include <QLayout>
#include <QPushButton>
#include <QSlider>

#include "qwt_plot.h"
#include "qwt_plot_curve.h"
#include "qwt_plot_picker.h"

class LWWidget;
class LWControls;

#include "lw_widget.h"


class LWControls : public QWidget
{
    Q_OBJECT

  private:
    LWWidget *m_widget;
    bool m_sliderupdating;
    double m_absmin, m_absmax, m_absrange;
    double m_curmin, m_curmax, m_currange;

    double m_range_x[2];
    double m_range_y[2];

    double m_histogram_x[256];
    double m_histogram_y[256];

  protected:
    QVBoxLayout *mainLayout;
    QPushButton *pushButton;
    QCheckBox *logscaleBox;
    QCheckBox *grayscaleBox;
    QCheckBox *cyclicBox;
    QSlider *minSlider;
    QSlider *maxSlider;
    QSlider *brtSlider;
    QSlider *ctrSlider;

    QwtPlot *histoPlot;
    QwtPlotCurve *histogram;
    QwtPlotCurve *histoRange;
    QwtPlotPicker *histoPicker;

    void setupUi();

  protected slots:
    void pickRange(const QwtDoubleRect &);
    void updateMinMax();
    void updateBrightness(int);
    void updateContrast(int);
    void setLogscale(bool);
    void setColorMap();

  public:
    LWControls(QWidget *parent = NULL);
    virtual ~LWControls();

    void updateNewData();
};

#endif
