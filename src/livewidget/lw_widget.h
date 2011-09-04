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

#ifndef LW_WIDGET_H
#define LW_WIDGET_H

#include <QPrinter>
#include <QPrintDialog>

#include <qwt_color_map.h>
#include <qwt_plot.h>
#include <qwt_plot_layout.h>
#include <qwt_plot_panner.h>
#include <qwt_plot_spectrogram.h>
#include <qwt_plot_zoomer.h>
#include <qwt_scale_widget.h>

#include "lw_data.h"


class LWZoomer : public QwtPlotZoomer
{
  protected:
    const QwtPlotSpectrogram *m_data;

  public:
    LWZoomer(QwtPlotCanvas *canvas, const QwtPlotSpectrogram *data);
    virtual ~LWZoomer();

    virtual QwtText trackerText(const QwtDoublePoint &pos) const;
};


class LWPlot : public QwtPlot
{
    Q_OBJECT

  private:
    void initPlot();
    void deinitPlot();
    
  protected:
    QwtPlotSpectrogram *m_spectro;
    QwtPlotPanner *m_panner;
    QwtPlotPicker *m_picker;
    LWZoomer *m_zoomer;

  public:
    LWPlot(QWidget *parent);
    virtual ~LWPlot();

    void changeRange();
    QwtPlotZoomer *getZoomer() { return m_zoomer; }
    QwtPlotPanner *getPanner() { return m_panner; }
    const QwtRasterData *getData() const { return &m_spectro->data(); }

    void setData(QwtRasterData *data);
    void setColorMap(QwtColorMap &map);

  public slots:
    void printPlot();
};


class LWWidget : public QWidget
{
    Q_OBJECT

  private:
    bool m_bForceReinit;
    void unload();

  protected:
    LWPlot *m_plot;
    LWData *m_data;

    ///int m_iMode;
    ///int m_iFolie, m_iZeitkanal;
    bool m_log10;

  public:
    LWWidget(QWidget *parent = NULL);
    virtual ~LWWidget();

    LWData *data() { return m_data; }
    void setData(LWData *data);

    void setCustomRange(double lower, double upper);
    void setColorMap(bool greyscale, bool cyclic);

    LWPlot *plot() { return m_plot; }

  public slots:
    void setLog10(bool bLog10);
    void setCustomRangeMin(int lower);
    void setCustomRangeMax(int lower);
    void setColormapGray(bool val);
    void setColormapCyclic(bool val);

    void updateGraph();
    void updateLabels();
};

#endif
