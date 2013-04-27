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

#ifndef __CASCADE_WIDGET__
#define __CASCADE_WIDGET__

#include "../plot/tofdata.h"
#include "../dialogs/cascadedialogs.h"
#include "../plot/plotter.h"

#include <QtGui/QWidget>


#define MODE_SLIDES		1
#define MODE_PHASES		2
#define MODE_CONTRASTS	3

#define MODE_SUMS			4
#define MODE_PHASESUMS		5
#define MODE_CONTRASTSUMS	6

#define MODE_OVERVIEW	10


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

		/// Image Container
		MainRasterData m_data2d;

		int m_iMode;
		int m_iFolie, m_iZeitkanal;
		bool m_bLog;

		//GraphDlg* m_pGraphDlg;
		RoiDlg* m_proidlg;
		BrowseDlg* m_pbrowsedlg;
		IntegrationDlg* m_pintdlg;
		RangeDlg* m_pRangeDlg;
		CountsVsImagesDlg* m_pCountsVsImagesDlg;
		ContrastsVsImagesDlg* m_pContrastsVsImagesDlg;

		//----------------------------------------------------------------------
		/// ROI curves for qwt
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

		/// load PAD or TOF from file
		bool LoadFile(const char* pcFile);

		/// load PAD from file
		bool LoadPadFile(const char* pcFile, bool bBinary);
		bool LoadPadFile(const char* pcFile);
		bool LoadPadFileTxt(const char* pcFile);

		/// load TOF from file
		bool LoadTofFile(const char* pcFile);

		/// load PAD from memory
		bool LoadPadMem(const char* pcMem, unsigned int iLen);

		/// load TOF from memory
		bool LoadTofMem(const char* pcMem, unsigned int iLen);

		/// get total counts of currently loaded PAD or TOF
		unsigned int GetCounts() const;

		/// loading of ROI elements
		bool LoadRoi(const char* pcFile);
		/// saving of ROI elements
		bool SaveRoi(const char* pcFile);

		void ForceReinit();

		TofImage* GetTof();
		TmpImage* GetTmpImg();
		MainRasterData& GetData2d();
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

		void SetAutoCountRange(bool bAuto);
		void SetCountRange(double dMin, double dMax);

		bool ToPDF(const char* pcDst) const;

	public slots:
		/// sum all foils and all time channels
		void viewOverview();
		/// show single foil
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
		void showBrowseDlg(const char* pcDir=0);
		void showIntegrationDlg();
		void showRangeDlg();
		void showCountsVsImagesDlg();
		void showContrastsVsImagesDlg();
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

		/// internal loopback method for the FileHasChanged signal
		void _FileHasChanged(const char* pcFileName);

	signals:
		void SumDlgSignal(const bool* pbKanaele, int iMode);

		/// emitted, when the file or its parameters (e.g. ROI) have changed
		void FileHasChanged(const char* pcFileName=0);
};

#endif
