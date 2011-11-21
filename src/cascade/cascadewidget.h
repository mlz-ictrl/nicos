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
//   Tobias Weber <tweber@frm2.tum.de>
//
// *****************************************************************************
/*
 * Cascade Widget
 * (Plotter initially based on "spectrogram" qwt sample code)
 */

#ifndef __CASCADE_WIDGET__
#define __CASCADE_WIDGET__

#include <QtGui/QWidget>

#include <qwt_plot.h>
#include <qwt_plot_zoomer.h>
#include <qwt_plot_panner.h>
#include <qwt_plot_picker.h>
#include <qwt_plot_spectrogram.h>
#include <qwt_color_map.h>
#include <qwt_symbol.h>

#include "tofdata.h"
#include "cascadedialogs.h"


#define MODE_SLIDES		1
#define MODE_PHASES		2
#define MODE_CONTRASTS	3

#define MODE_SUMS			4
#define MODE_PHASESUMS		5
#define MODE_CONTRASTSUMS	6


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

		void SetData(Data2D* pData, bool bUpdate=true);
		const QwtRasterData* GetData() const;

		void SetColorMap(bool bCyclic);

		void InitPlot();
		void DeinitPlot();

	public slots:
		void printPlot();
		virtual void replot();
};



class CascadeWidget : public QWidget
{
Q_OBJECT
	private:
		bool m_bForceReinit;

	protected:
		Plot *m_pPlot;

		// PAD
		PadImage *m_pPad;

		// TOF
		TofImage *m_pTof;
		TmpImage *m_pTmpImg;

		// Image Container
		Data2D m_data2d;

		int m_iMode;
		int m_iFolie, m_iZeitkanal;
		bool m_bLog;

		RoiDlg* m_proidlg;
		BrowseDlg* m_pbrowsedlg;
		IntegrationDlg* m_pintdlg;

		//----------------------------------------------------------------------
		// ROI curves for qwt
		std::vector<QwtPlotCurve*> m_vecRoiCurves;
		void UpdateRoiVector();
		void ClearRoiVector();

	public:
		void ClearRoi();
		void RedrawRoi();

		//----------------------------------------------------------------------

	public:
		CascadeWidget(QWidget *parent=NULL);
		virtual ~CascadeWidget();

		void Unload();
		bool IsTofLoaded() const;
		bool IsPadLoaded() const;
		void* NewPad();
		void* NewTof();

		// load PAD or TOF from file
		bool LoadFile(const char* pcFile);

		// load PAD from file
		bool LoadPadFile(const char* pcFile);

		// load TOF from file
		bool LoadTofFile(const char* pcFile);

		// load PAD from memory
		bool LoadPadMem(const char* pcMem, unsigned int iLen);

		// load TOF from memory
		bool LoadTofMem(const char* pcMem, unsigned int iLen);

		// get total counts of currently loaded PAD or TOF
		unsigned int GetCounts() const;

		// loading/saving of ROI elements
		bool LoadRoi(const char* pcFile);
		bool SaveRoi(const char* pcFile);

		void ForceReinit();

		TofImage* GetTof();
		TmpImage* GetTmpImg();
		Data2D& GetData2d();
		PadImage* GetPad();
		Plot* GetPlot();
		unsigned int* GetRawData();

		bool GetLog10();
		int GetFoil() const;
		int GetTimechannel() const;

		void SetMode(int iMode);
		int GetMode();

		void SetRoiDrawMode(int iMode);

		Roi* GetCurRoi();
		bool IsRoiInUse();
		void UseRoi(bool bUse);

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
		void showRoiDlg();
		void showBrowseDlg(const char* pcDir=".");
		void showIntegrationDialog();
		///////////////////////////////////////

		void SetLog10(bool bLog10);
		void SetFoil(int iFolie);
		void SetTimechannel(int iKanal);

		void UpdateGraph();
		void UpdateLabels();
		void UpdateRange();

		void SumDlgSlot(const bool *pbKanaele, int iMode);

	protected slots:
		void RoiDlgAccepted(QAbstractButton*);
		void RoiHasChanged();

	signals:
		void SumDlgSignal(const bool* pbKanaele, int iMode);

		// emitted, when the file or its parameters (e.g. ROI) have changed
		void FileHasChanged(const char* pcFileName=0);
};

#endif
