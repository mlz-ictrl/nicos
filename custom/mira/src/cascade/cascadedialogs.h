// *****************************************************************************
// NICOS, the Networked Instrument Control System of the FRM-II
// Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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
// Cascade sub dialogs

#ifndef __CASCADE_DIALOGE__
#define __CASCADE_DIALOGE__

#include <qwt_plot.h>
#include <qwt_plot_grid.h>
#include <qwt_plot_zoomer.h>
#include <qwt_plot_panner.h>
#include <qwt_plot_layout.h>
#include <qwt_plot_marker.h>
#include <qwt_interval_data.h>
#include <qwt_plot_curve.h>
#include <qwt_plot_spectrogram.h>
#include <qwt_scale_widget.h>
#include <qwt_scale_draw.h>
#include <qwt_color_map.h>
#include <qwt_legend.h>
#include <qwt_legend_item.h>
#include <qwt_symbol.h>

#include <QtGui/QPainter>
#include <QtGui/QDialog>

#include "ui_graphdlg.h"
#include "ui_sumdialog.h"
#include "ui_calibrationdlg.h"
#include "ui_serverdlg.h"
#include "ui_servercfgdlg.h"
#include "ui_commanddlg.h"
#include "ui_roidlg.h"
#include "ui_browsedlg.h"
#include "ui_integrationdlg.h"
#include "ui_rangedlg.h"
#include "ui_countsvsimagesdlg.h"
#include "ui_contrastsvsimagesdlg.h"
#include "ui_batchdlg.h"

#include "histogram_item.h"
#include "bins.h"
#include "globals.h"
#include "tofloader.h"
#include "ErrorBarPlotCurve.h"
#include "roi.h"

class CascadeWidget;


#define MODE_PAD 1
#define MODE_TOF 2

// *********************************************************************
class CommandDlg : public QDialog, public Ui::CommandDlg
{
	Q_OBJECT

	protected:

	protected slots:

	public:
		CommandDlg(QWidget *pParent);
		virtual ~CommandDlg();
};
// ********************************************************************



// *********************************************************************
class CalibrationDlg : public QDialog, public Ui::CalibrationDlg
{
	Q_OBJECT

	protected:
		QwtPlotGrid *m_pgrid;
		HistogramItem *m_phistogram;

	protected slots:

	public:
		CalibrationDlg(QWidget *pParent, const Bins& bins);
		virtual ~CalibrationDlg();
};
// ********************************************************************


// ************************* Graph-Dialog *****************************
class GraphDlg : public QDialog, public Ui::GraphDlg
{
	Q_OBJECT

	private:
		void Init(int iFolie);

	protected:
		TofImage *m_pTofImg;
		ErrorBarPlotCurve m_curve;
		QwtPlotCurve m_curvefit, m_curvetotal;
		QwtLegend *m_plegend;
		QwtPlotGrid *m_pgrid;
		void UpdateGraph(void);

	protected slots:
		void Foilchanged(int iVal);
		void printPlot();
		void checkBoxDoFitChanged(int state);

	public:
		GraphDlg(QWidget *pParent, TofImage* pTof);
		GraphDlg(QWidget *pParent, TofImage* pTof, int iFolie);
		virtual ~GraphDlg();
};
// *****************************************************************************


// ************************* Summierungs-Dialog mit Zeitkanälen ****************
class SumDlg : public QDialog, public Ui::FolienSummeDlg
{
	Q_OBJECT

	protected:
		QTreeWidgetItem** m_pTreeItemsFolien;
		QTreeWidgetItem** m_pTreeItems;
		TofImage *m_pTof;
		int m_iMode;

	protected slots:
		void ShowIt();
		void SelectAll();
		void SelectNone();
		void TreeWidgetClicked(QTreeWidgetItem *item, int column);

	public:
		SumDlg(QWidget *pParent);
		virtual ~SumDlg();
		void SetMode(int iMode);

	signals:
		void SumSignal(const bool *pbKanaele, int iMode);
};
// *****************************************************************************


// ************************* Summierungs-Dialog ohne Zeitkanäle ****************
class SumDlgNoChannels : public QDialog, public Ui::FolienSummeDlg
{
	Q_OBJECT

	protected:
		QTreeWidgetItem** m_pTreeItemsFolien;
		TofImage *m_pTof;
		int m_iMode;

	protected slots:
		void ShowIt();
		void SelectAll();
		void SelectNone();

	public:
		SumDlgNoChannels(QWidget *pParent);
		virtual ~SumDlgNoChannels();
		void SetMode(int iMode);

	signals:
		void SumSignal(const bool *pbKanaele, int iMode);
};
// *****************************************************************************


// ************************* Server-Dialog *************************************
class ServerDlg : public QDialog, public Ui::dialogServer
{
	Q_OBJECT

	protected:

	protected slots:

	public:
		ServerDlg(QWidget *pParent);
		virtual ~ServerDlg();
};
// *****************************************************************************


// ************************* Server-Dialog *************************************
class ServerCfgDlg : public QDialog, public Ui::ServerConfigDlg
{
	Q_OBJECT

	protected:
		static double s_dLastTime;
		static unsigned int s_iXRes, s_iYRes, s_iTRes;
		static int s_iMode;
		static bool s_bUsePseudoComp;

	protected slots:
		void toggledmode(bool bChecked);

	public:
		ServerCfgDlg(QWidget *pParent);
		virtual ~ServerCfgDlg();

		double GetMeasTime();
		unsigned int GetXRes();
		unsigned int GetYRes();
		unsigned int GetTRes();
		int GetMode();
		bool GetPseudoComp();


		static void SetStatXRes(int iXRes);
		static void SetStatYRes(int iYRes);
		static void SetStatTRes(int iTRes);
		static void SetStatMode(int iMode);
		static void SetStatTime(double dTime);
		static void SetStatComp(bool bComp);

		static int GetStatXRes();
		static int GetStatYRes();
		static int GetStatTRes();
		static int GetStatMode();
		static double GetStatTime();
		static bool GetStatComp();
};


// ************************* Roi-Dialog ****************************************

class RoiDlg : public QDialog, public Ui::RoiDlg
{
	Q_OBJECT

	protected:
		CascadeWidget *m_pwidget;
		Roi *m_pRoi;
		int m_iCurrentItem;

		void NewElement(RoiElement* pNewElem);
		void Deinit();

	public:
		RoiDlg(CascadeWidget *pParent);
		virtual ~RoiDlg();

		void SetRoi(const Roi* pRoi);
		const Roi* GetRoi(void) const;
		void ClearList();

	public slots:
		void ItemSelected();
		void ValueChanged(QTableWidgetItem *pItem);

		void NewCircle();
		void NewEllipse();
		void NewCircleRing();
		void NewCircleSeg();
		void NewRect();

		void DeleteItem();
		void CopyItem();
		void Fit();
};

// *****************************************************************************



// ************************* Browse Dialog *************************************

class BrowseDlg : public QDialog, public Ui::BrowseDlg
{
	Q_OBJECT

	protected:
		CascadeWidget *m_pwidget;

	protected slots:
		void SelectDir();
		void SelectedFile();

	public:
		BrowseDlg(CascadeWidget *pParent, const char* pcDir=".");
		virtual ~BrowseDlg();

		void SetDir(const QString& strDir);
};

// *****************************************************************************





// ************************* Integration Dialog ********************************

class IntegrationDlg : public QDialog, public Ui::IntegrationDlg
{
	Q_OBJECT

	protected:
		CascadeWidget *m_pwidget;
		QwtPlotCurve m_curve;
		QwtPlotGrid *m_pgrid;

		QwtPlotZoomer *m_pzoomer;
		QwtPlotPanner *m_ppanner;

		bool m_bAutoUpdate;

		TmpImage GetRoiImage();

	public:
		IntegrationDlg(CascadeWidget *pParent);
		virtual ~IntegrationDlg();

	public slots:
		void UpdateGraph();
		void UseBeamCenter();
		void UseImageCenter();
		void SetLog10(bool);
};

// *****************************************************************************




// ************************* Range Dialog **************************************

class RangeDlg : public QDialog, public Ui::RangeDlg
{
	Q_OBJECT

	protected:
		CascadeWidget *m_pWidget;

		// don't write changes back to m_pWidget
		bool m_bReadOnly;

	public:
		RangeDlg(CascadeWidget *pParent);
		virtual ~RangeDlg();

		void Update();
		void SetReadOnly(bool bReadOnly);

	public slots:
		void SetAutoRange(bool bAuto);

	protected slots:
		void RangeChanged();
};

// *****************************************************************************




// ************************* Counts vs. Images Dialog **************************

class CountsVsImagesDlg : public QDialog, public Ui::CountsVsImagesDlg
{
	Q_OBJECT

	protected:
		CascadeWidget *m_pwidget;

		QwtPlotCurve m_curve;
		QwtPlotGrid *m_pgrid;
		QwtPlotZoomer *m_pzoomer;
		QwtPlotPanner *m_ppanner;

	public:
		CountsVsImagesDlg(CascadeWidget *pParent);
		virtual ~CountsVsImagesDlg();

	protected slots:
		void LoadRoi();
		void SetRoiUseCurrent(bool bCur);
		void AddFile();
		void DeleteFile();
		void RoiGroupToggled();

	public slots:
		void UpdateGraph();
};

// *****************************************************************************




// ************************* Contrasts vs. Images Dialog ***********************

class ContrastsVsImagesDlg : public QDialog, public Ui::ContrastsVsImagesDlg
{
	Q_OBJECT

	protected:
		CascadeWidget *m_pwidget;

		ErrorBarPlotCurve m_curve;
		QwtPlotGrid *m_pgrid;
		QwtPlotZoomer *m_pzoomer;
		QwtPlotPanner *m_ppanner;

	public:
		ContrastsVsImagesDlg(CascadeWidget *pParent);
		virtual ~ContrastsVsImagesDlg();

	protected slots:
		void LoadRoi();
		void SetRoiUseCurrent(bool bCur);
		void AddFile();
		void DeleteFile();
		void RoiGroupToggled();

		void AddFile_underground();
		void DeleteFile_underground();		

	public slots:
		void UpdateGraph();
};

// *****************************************************************************



// ************************* Batch Job Dialog **********************************

class BatchDlg : public QDialog, public Ui::BatchDlg
{
	Q_OBJECT

	protected:
		CascadeWidget *m_pwidget;

		void ConvertToPDF(const char* pcSrc, const char* pcDst);
		void ConvertToBinary(const char* pcSrc, const char* pcDst);

	protected slots:
		void SelectSrcDir();
		void SelectDstDir();
		void Start();

	public:
		BatchDlg(CascadeWidget *pParent);
		virtual ~BatchDlg();
};

// *****************************************************************************

#endif
