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

%Module livewidget 0

%Import QtGui/QtGuimod.sip
%Import QtCore/QtCoremod.sip
%Import Qwt5/QwtModule.sip


class LWData
{
%TypeHeaderCode
#include "../lw_data.h"
%End
  public:
    LWData(const LWData &other);
    LWData(int width, int height, int depth, const char *data);
    LWData(int width, int height, int depth,
           const char *format, const char *data);

    int width() const;
    int height() const;
    int depth() const;
    double min() const;
    double max() const;

    int currentZ() const;
    virtual void setCurrentZ(int val);

    bool isLog10() const;
    virtual void setLog10(bool val);

    bool hasCustomRange() const;
    double customRangeMin() const;
    double customRangeMax() const;
    virtual void setCustomRange(double lower, double upper);

    virtual double value(double x, double y) const;
    virtual double valueRaw(int x, int y) const;
    virtual double valueRaw(int x, int y, int z) const;

    virtual void histogram(int bins, QVector<double> **xs,
                           QVector<double> **ys) const;
};


class LWZoomer : QwtPlotZoomer
{
%TypeHeaderCode
#include "../lw_widget.h"
%End
  public:
    LWZoomer(QwtPlotCanvas *canvas, const QwtPlotSpectrogram *spectro);
};


class LWPlot : QwtPlot
{
%TypeHeaderCode
#include "../lw_plot.h"
%End
  public:
    LWPlot(QWidget *parent);

    void updateRange();
    LWZoomer *getZoomer();
    QwtPlotPanner *getPanner();
    const QwtRasterData *getData() const;

    void setData(QwtRasterData *data);
    void setColorMap(QwtColorMap &map);

  public slots:
    void printPlot();
};


class LWWidget : QWidget
{
%TypeHeaderCode
#include "../lw_widget.h"
%End
  public:
    LWWidget(QWidget *parent = NULL);
    virtual ~LWWidget();

    LWPlot *plot();

    LWData *data();
    void setData(LWData *data /Transfer/);

    bool isLog10() const;
    bool keepAspect() const;
    bool controlsVisible() const;

    void setCustomRange(double lower, double upper);
    void setStandardColorMap(bool greyscale, bool cyclic);
    void setAxisLabels(const char *xaxis, const char *yaxis);

  public slots:
    void setLog10(bool val);
    void setKeepAspect(bool val);
    void setControlsVisible(bool val);

    void updateGraph();
    void updateLabels();

  signals:
    void dataUpdated(LWData *data);
};

%UnitCode
#include "../lw_common.h"
%End

enum LWCtrl
{
    Logscale,
    Grayscale,
    Cyclic,
    CreateProfile,
    Histogram,
    MinimumMaximum,
    BrightnessContrast
};
