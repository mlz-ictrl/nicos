
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

#ifndef LW_PLOT_H
#define LW_PLOT_H

#include <QPrinter>
#include <QPrintDialog>

#include <qwt_color_map.h>
#include <qwt_plot.h>
#include <qwt_plot_layout.h>
#include <qwt_plot_panner.h>
#include <qwt_plot_rescaler.h>
#include <qwt_plot_spectrogram.h>
#include <qwt_plot_zoomer.h>
#include <qwt_plot_grid.h>
#include <qwt_scale_widget.h>

#include "lw_data.h"


class LWZoomer : public QwtPlotZoomer
{
  private:
    bool m_aspect;

  protected:
    const QwtPlotSpectrogram *m_spectro;

  public:
    LWZoomer(QwtPlotCanvas *canvas, const QwtPlotSpectrogram *spectro);
    virtual ~LWZoomer();

    bool isKeepAspect() const { return m_aspect; }
    void setKeepAspect(bool val);

    virtual void zoom(const QwtDoubleRect &rect);
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
    QwtPlotRescaler *m_rescaler;
    QwtPlotGrid *m_grid;
    LWZoomer *m_zoomer;
    int m_scale_width;
    int m_scale_height;

  public:
    LWPlot(QWidget *parent);
    virtual ~LWPlot();

    void updateRange();
    LWZoomer *getZoomer() { return m_zoomer; }
    QwtPlotPanner *getPanner() { return m_panner; }
    QwtPlotPicker *getPicker() { return m_picker; }
    const QwtRasterData *getData() const { return &m_spectro->data(); }

    void setData(QwtRasterData *data);
    void setGrid(bool val);
    void setColorMap(QwtColorMap &map);

    bool hasGrid() { return m_grid->isVisible(); }

  public slots:
    void printPlot();
};
#endif
