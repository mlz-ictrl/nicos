// *****************************************************************************
// Module:
//   $Id$
//
// Author:
//   Tobias Weber <tweber@frm2.tum.de>
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

#ifndef __CASCADE_WIDGET__
#define __CASCADE_WIDGET__

#include <QtGui/QWidget>

#include <qwt/qwt_plot.h>
#include <qwt/qwt_plot_grid.h>
#include <qwt/qwt_plot_zoomer.h>
#include <qwt/qwt_plot_panner.h>
#include <qwt/qwt_plot_layout.h>
#include <qwt/qwt_plot_marker.h>
#include <qwt/qwt_plot_rescaler.h>
#include <qwt/qwt_interval_data.h>
#include <qwt/qwt_plot_curve.h>
#include <qwt/qwt_plot_spectrogram.h>
#include <qwt/qwt_scale_widget.h>
#include <qwt/qwt_scale_draw.h>
#include <qwt/qwt_color_map.h>
#include <qwt/qwt_legend.h>
#include <qwt/qwt_legend_item.h>
#include <qwt/qwt_symbol.h>

#include "tofdata.h"


#define MODE_SLIDES		1
#define MODE_PHASES		2
#define MODE_CONTRASTS	3

#define MODE_SUMS			4
#define MODE_PHASESUMS		5
#define MODE_CONTRASTSUMS	6



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

	public:
		Plot(QWidget *parent);
		virtual ~Plot();

		void ChangeRange();
		QwtPlotZoomer* GetZoomer();
		QwtPlotPanner* GetPanner();

		void SetData(QwtRasterData* pData);
		const QwtRasterData* GetData() const;

		void SetColorMap(bool bCyclic);

		void InitPlot();
		void DeinitPlot();

	public slots:
		void printPlot();
};



class CascadeWidget : public QWidget
{
Q_OBJECT
	private:
		bool m_bForceReinit;

	protected:
		Plot *m_pPlot;

		// PAD
		PadData *m_pPad;

		// TOF
		TofImage *m_pTof;
		Data2D *m_pdata2d;

		int m_iMode;
		int m_iFolie, m_iZeitkanal;
		bool m_bLog;

	public:
		CascadeWidget(QWidget *parent=NULL);
		virtual ~CascadeWidget();

		void Unload();
		bool IsTofLoaded() const;
		bool IsPadLoaded() const;
		void* NewPad();
		void* NewTof(int iCompression = TOF_COMPRESSION_USEGLOBCONFIG);

		// load PAD from file
		bool LoadPadFile(const char* pcFile);

		// load TOF from file
		bool LoadTofFile(const char* pcFile);

		// load PAD from memory
		bool LoadPadMem(const char* pcMem, unsigned int iLen);

		// load TOF from memory
		bool LoadTofMem(const char* pcMem, unsigned int iLen);

		TofImage* GetTof();
		Data2D* GetData2d();
		PadData* GetPad();
		Plot* GetPlot();
		unsigned int* GetRawData();

		bool GetLog10();
		int GetFoil() const;
		int GetTimechannel() const;

		void SetMode(int iMode);
		int GetMode();

	public slots:
		// sum all foils and all time channels
		void viewOverview();
		// show single foil
		void viewSlides();
		void viewPhases();
		void viewContrasts();

		void viewFoilSums(const bool* pbKanaele);
		void viewPhaseSums(const bool* pbFolien);
		void viewContrastSums(const bool* pbFolien);

		// dialogs ////////////////////////////
		void showCalibrationDlg(int iNumBins);
		void showGraphDlg();
		void showSumDlg();
		///////////////////////////////////////

		void SetLog10(bool bLog10);
		void SetFoil(int iFolie);
		void SetTimechannel(int iKanal);

		void UpdateGraph();
		void UpdateLabels();
		void UpdateRange();

		void SumDlgSlot(const bool *pbKanaele, int iMode);

	signals:
		void SumDlgSignal(const bool* pbKanaele, int iMode);
};

#endif
