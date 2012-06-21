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

#ifndef LW_PROFILE_H
#define LW_PROFILE_H

#include <QMainWindow>

class LWWidget;

#include "lw_widget.h"


class LWProfileWindow : public QMainWindow
{
    Q_OBJECT

  private:
    LWWidget *m_widget;
    QwtPlot *m_plot;
    QwtPlotCurve *m_curve;
    QwtPlotZoomer *m_zoomer;
    QwtPlotPicker *m_picker;
    double *m_data_x, *m_data_y;
    int m_type;

  protected slots:
    void pickerSelected(const QwtDoublePoint &point);

  public:
    LWProfileWindow(QWidget *parent, LWWidget *widget);
    virtual ~LWProfileWindow();

    void update(LWData *data, double *px, double *py, int width, int bins, int type);
};

#endif
