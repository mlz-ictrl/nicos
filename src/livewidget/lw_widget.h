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

#ifndef LW_WIDGET_H
#define LW_WIDGET_H

class LWControls;

#include "lw_plot.h"
#include "lw_controls.h"
#include "lw_common.h"

#define INSTR_NONE    0
#define INSTR_TOFTOF  1


class LWWidget : public QWidget
{
    Q_OBJECT

    friend class LWProfileWindow;

  private:
    bool m_bForceReinit;
    int m_instr;
    void *m_instr_data;
    void unload();

  protected:
    LWData *m_data;
    LWPlot *m_plot;
    LWControls *m_controls;

    bool m_log10;

  public:
    LWWidget(QWidget *parent = NULL);
    virtual ~LWWidget();

    void setInstrumentOption(const char *instr);
    int instrument();

    LWPlot *plot() { return m_plot; }

    LWData *data() { return m_data; }
    void setData(LWData *data);

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
    void setControls(LWCtrl which);

    void updateGraph(bool newdata=true);
    void updateLabels();

  signals:
    void dataUpdated(LWData *data);
    void profilePointPicked(int type, double x, double y);
    void profileUpdate(int type, int nbins, void *dx, void *dy);
};

#endif
