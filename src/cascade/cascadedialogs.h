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
// Cascade-Unterdialoge

#ifndef __CASCADE_DIALOGE__
#define __CASCADE_DIALOGE__

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

#include <QtGui/QPainter>
#include <QDialog>

#include "ui_graphdlg.h"
#include "ui_sumdialog.h"
#include "ui_calibrationdlg.h"
#include "ui_serverdlg.h"
#include "ui_servercfgdlg.h"
#include "histogram_item.h"
#include "bins.h"
#include "globals.h"
#include "tofloader.h"
#include "ErrorBarPlotCurve.h"


#define MODE_PAD 1
#define MODE_TOF 2


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
		void Init(int iROIx1, int iROIx2, int iROIy1, int iROIy2, int iFolie);

	protected:
		TofImage *m_pTofImg;
		ErrorBarPlotCurve m_curve;
		QwtPlotCurve m_curvefit, m_curvetotal;
		QwtLegend *m_plegend;
		QwtPlotGrid *m_pgrid;

		void UpdateGraph(void);

	protected slots:
		void ROIy1changed(int iVal);
		void ROIy2changed(int iVal);
		void ROIx1changed(int iVal);
		void ROIx2changed(int iVal);
		void Foilchanged(int iVal);
		void Phasechanged(double dVal);

	public:
		GraphDlg(QWidget *pParent, TofImage* pTof);
		GraphDlg(QWidget *pParent, TofImage* pTof, int iROIx1, int iROIx2,
												   int iROIy1, int iROIy2,
												   int iFolie);
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

#endif
