// *****************************************************************************
// NICOS, the Networked Instrument Control System of the FRM-II
// Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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
//   Tobias Weber <tweber@frm2.tum.de>
//
// *****************************************************************************
//
// Plotter initially based on "spectrogram" qwt sample code
//

#ifndef __CASC_PLOTTER__
#define __CASC_PLOTTER__

#include <qwt_plot.h>
#include <qwt_plot_zoomer.h>
#include <qwt_plot_panner.h>
#include <qwt_plot_picker.h>
#include <qwt_plot_spectrogram.h>
#include <qwt_color_map.h>
#include <qwt_symbol.h>

#include "../auxiliary/roi.h"
#include "tofdata.h"


#define ROI_DRAW_NONE		0
#define ROI_DRAW_RECT		1
#define ROI_DRAW_CIRC		2
#define ROI_DRAW_CIRCRING 	3
#define ROI_DRAW_CIRCSEG 	4
#define ROI_DRAW_ELLIPSE	5
#define ROI_DRAW_POLYGON	6


class MainPicker : public QwtPlotPicker
{
	Q_OBJECT

	protected:
		int m_iRoiDrawMode;
		Roi *m_pCurRoi;

	protected slots:
		void selectedRect(const QwtDoubleRect& rect);
		void selectedPoly(const QwtArray<QwtDoublePoint>& poly);

	public:
		MainPicker(QwtPlotCanvas* pcanvas);
		virtual ~MainPicker();

		virtual QwtText trackerText(const QwtDoublePoint &pos) const;

		void SetRoiDrawMode(int iMode);
		int GetRoiDrawMode() const;
		void SetCurRoi(Roi* pRoi);

	signals:
		void RoiHasChanged();
};


class MainZoomer : public QwtPlotZoomer
{
	protected:
		const QwtPlotSpectrogram* m_pData;

	public:
		MainZoomer(QwtPlotCanvas *canvas, const QwtPlotSpectrogram* pData);
		virtual ~MainZoomer();

		virtual QwtText trackerText(const QwtDoublePoint &pos) const;
};


class MainPanner : public QwtPlotPanner
{
	protected:

	public:
		MainPanner(QwtPlotCanvas *canvas);
		virtual ~MainPanner();
};


class Plot : public QwtPlot
{
	Q_OBJECT

	protected:
		QwtPlotSpectrogram *m_pSpectrogram;
		MainZoomer* m_pZoomer;
		MainPanner* m_pPanner;

		MainPicker* m_pRoiPicker;

		const BasicImage* m_pImage;

	public:
		Plot(QWidget *parent);
		virtual ~Plot();

		void ChangeRange();
		void ChangeRange_xy();

		QwtPlotZoomer* GetZoomer();
		QwtPlotPanner* GetPanner();
		QwtPlotPicker* GetRoiPicker();

		void SetData(MainRasterData* pData, bool bUpdate=true);
		const QwtRasterData* GetData() const;

		void SetColorMap(bool bCyclic);

		void InitPlot();
		void DeinitPlot();

	public slots:
		void printPlot();
		virtual void replot();
};

#endif
