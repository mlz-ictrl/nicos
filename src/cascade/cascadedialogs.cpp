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
// Cascade-Unterdialoge

#include "cascadedialogs.h"
#include <stdio.h>


// ************************* Kalibrierungs-Dialog *********************
CalibrationDlg::CalibrationDlg(QWidget *pParent, const Bins& bins) : QDialog(pParent), m_pgrid(0)
{
	setupUi(this);
	qwtPlot->setCanvasBackground(QColor(Qt::white));
	
	const QwtArray<QwtDoubleInterval>& intervals = bins.GetIntervals();
	const QwtArray<double>& values = bins.GetValues();
	
	m_pgrid = new QwtPlotGrid;
	m_pgrid->enableXMin(true);
	m_pgrid->enableYMin(true);
	m_pgrid->setMajPen(QPen(Qt::black, 0, Qt::DotLine));
	m_pgrid->setMinPen(QPen(Qt::gray, 0 , Qt::DotLine));
	m_pgrid->attach(qwtPlot);
	
	m_phistogram = new HistogramItem();
	m_phistogram->setColor(Qt::black);
	m_phistogram->attach(qwtPlot);
	
	qwtPlot->setAxisScale(QwtPlot::xBottom, 0., 360.);
	qwtPlot->setAxisScale(QwtPlot::yLeft, 0.0, bins.GetMaxVal());
	qwtPlot->axisWidget(QwtPlot::xBottom)->setTitle("Phase [DEG]");
	qwtPlot->axisWidget(QwtPlot::yLeft)->setTitle("Number");
	
	m_phistogram->setData(QwtIntervalData(intervals, values));
	qwtPlot->replot();
}

CalibrationDlg::~CalibrationDlg()
{
	if(m_pgrid) delete m_pgrid;
}
// ********************************************************************




// ************************* Summierungs-Dialog mit Zeitkanälen ***********************
void SumDlg::ShowIt()
{
	bool *pbChecked = new bool[Config_TofLoader::FOIL_COUNT*Config_TofLoader::IMAGES_PER_FOIL];
	for(int iFolie=0; iFolie<Config_TofLoader::FOIL_COUNT; ++iFolie)
	{
		for(int iKanal=0; iKanal<Config_TofLoader::IMAGES_PER_FOIL; ++iKanal)
		{
			bool bChecked = (m_pTreeItems[iFolie*Config_TofLoader::IMAGES_PER_FOIL + iKanal]->checkState(0)==Qt::Checked);
			pbChecked[iFolie*Config_TofLoader::IMAGES_PER_FOIL + iKanal] = bChecked;
		}
	}
	emit SumSignal(pbChecked, m_iMode);
	delete[] pbChecked;
}

void SumDlg::SelectAll()
{
	for(int iFolie=0; iFolie<Config_TofLoader::FOIL_COUNT; ++iFolie)
	{
		m_pTreeItemsFolien[iFolie]->setCheckState(0,Qt::Checked);
		for(int iKanal=0; iKanal<Config_TofLoader::IMAGES_PER_FOIL; ++iKanal)
			m_pTreeItems[iFolie*Config_TofLoader::IMAGES_PER_FOIL + iKanal]->setCheckState(0,Qt::Checked);
	}
}

void SumDlg::SelectNone()
{
	for(int iFolie=0; iFolie<Config_TofLoader::FOIL_COUNT; ++iFolie)
	{
		m_pTreeItemsFolien[iFolie]->setCheckState(0,Qt::Unchecked);
		for(int iKanal=0; iKanal<Config_TofLoader::IMAGES_PER_FOIL; ++iKanal)
			m_pTreeItems[iFolie*Config_TofLoader::IMAGES_PER_FOIL + iKanal]->setCheckState(0,Qt::Unchecked);
	}
}

void SumDlg::TreeWidgetClicked(QTreeWidgetItem *item, int column)
{
	int iFolie;
	for(iFolie=0; iFolie<Config_TofLoader::FOIL_COUNT; ++iFolie)
		if(m_pTreeItemsFolien[iFolie]==item) break;
	if(iFolie==Config_TofLoader::FOIL_COUNT) return;	// nicht auf Parent geklickt
	
	for(int iKanal=0; iKanal<Config_TofLoader::IMAGES_PER_FOIL; ++iKanal)
		m_pTreeItems[iFolie*Config_TofLoader::IMAGES_PER_FOIL + iKanal]->setCheckState(0,m_pTreeItemsFolien[iFolie]->checkState(0));
}

SumDlg::SumDlg(QWidget *pParent) : QDialog(pParent)
{
	setupUi(this);
	
	m_pTreeItemsFolien = new QTreeWidgetItem*[Config_TofLoader::FOIL_COUNT];
	m_pTreeItems = new QTreeWidgetItem*[Config_TofLoader::FOIL_COUNT*Config_TofLoader::IMAGES_PER_FOIL];

	for(int iFolie=0; iFolie<Config_TofLoader::FOIL_COUNT; ++iFolie)
	{
		m_pTreeItemsFolien[iFolie] = new QTreeWidgetItem(treeWidget);
		char pcName[256];
		sprintf(pcName, "Foil %d", iFolie+1);
		m_pTreeItemsFolien[iFolie]->setText(0, pcName);
		m_pTreeItemsFolien[iFolie]->setCheckState(0, Qt::Unchecked);
		
		for(int iKanal=0; iKanal<Config_TofLoader::IMAGES_PER_FOIL; ++iKanal)
		{
			m_pTreeItems[iFolie*Config_TofLoader::IMAGES_PER_FOIL + iKanal] = new QTreeWidgetItem(m_pTreeItemsFolien[iFolie]);
			m_pTreeItems[iFolie*Config_TofLoader::IMAGES_PER_FOIL + iKanal]->setCheckState(0, Qt::Unchecked);
			sprintf(pcName, "Time Channel %d", iKanal+1);
			m_pTreeItems[iFolie*Config_TofLoader::IMAGES_PER_FOIL + iKanal]->setText(0, pcName);
		}
	}
	
	connect(treeWidget, SIGNAL(itemClicked(QTreeWidgetItem *, int)), this, SLOT(TreeWidgetClicked(QTreeWidgetItem *, int)));
	connect(pushButtonShow, SIGNAL(clicked()), this, SLOT(ShowIt()));
	connect(pushButtonSelectAll, SIGNAL(clicked()), this, SLOT(SelectAll()));
	connect(pushButtonSelectNone, SIGNAL(clicked()), this, SLOT(SelectNone()));
}

SumDlg::~SumDlg()
{
	delete[] m_pTreeItemsFolien; m_pTreeItemsFolien = 0;
	delete[] m_pTreeItems; m_pTreeItems = 0;
}

void SumDlg::SetMode(int iMode) { m_iMode = iMode; }
// ********************************************************************


// ************************* Summierungs-Dialog ohne Zeitkanäle ***********************
void SumDlgNoChannels::ShowIt()
{
	bool *pbChecked = new bool[Config_TofLoader::FOIL_COUNT];
	for(int iFolie=0; iFolie<Config_TofLoader::FOIL_COUNT; ++iFolie)
	{
		bool bChecked = (m_pTreeItemsFolien[iFolie]->checkState(0)==Qt::Checked);
		pbChecked[iFolie] = bChecked;
	}
	emit SumSignal(pbChecked, m_iMode);
	delete[] pbChecked;
}

void SumDlgNoChannels::SelectAll()
{
	for(int iFolie=0; iFolie<Config_TofLoader::FOIL_COUNT; ++iFolie)
		m_pTreeItemsFolien[iFolie]->setCheckState(0,Qt::Checked);
}

void SumDlgNoChannels::SelectNone()
{
	for(int iFolie=0; iFolie<Config_TofLoader::FOIL_COUNT; ++iFolie)
		m_pTreeItemsFolien[iFolie]->setCheckState(0,Qt::Unchecked);
}

SumDlgNoChannels::SumDlgNoChannels(QWidget *pParent) : QDialog(pParent)
{
	setupUi(this);
	m_pTreeItemsFolien = new QTreeWidgetItem*[Config_TofLoader::FOIL_COUNT];

	for(int iFolie=0; iFolie<Config_TofLoader::FOIL_COUNT; ++iFolie)
	{
		m_pTreeItemsFolien[iFolie] = new QTreeWidgetItem(treeWidget);
		char pcName[256];
		sprintf(pcName, "Foil %d", iFolie+1);
		m_pTreeItemsFolien[iFolie]->setText(0, pcName);
		m_pTreeItemsFolien[iFolie]->setCheckState(0, Qt::Unchecked);
	}
	
	connect(pushButtonShow, SIGNAL(clicked()), this, SLOT(ShowIt()));
	connect(pushButtonSelectAll, SIGNAL(clicked()), this, SLOT(SelectAll()));
	connect(pushButtonSelectNone, SIGNAL(clicked()), this, SLOT(SelectNone()));
}

SumDlgNoChannels::~SumDlgNoChannels()
{
	delete[] m_pTreeItemsFolien; m_pTreeItemsFolien = 0;
}

void SumDlgNoChannels::SetMode(int iMode) { m_iMode = iMode; }
// ********************************************************************



// ************************* Zeug für Graph-Dialog ***********************
void GraphDlg::UpdateGraph(void)
{
	// Messpunkte für eine Folie
	TmpGraph tmpGraph;
	m_pTofImg->GetGraph(spinBoxROIx1->value(),spinBoxROIx2->value(),spinBoxROIy1->value(),spinBoxROIy2->value(),spinBoxFolie->value()-1, &tmpGraph);
	
	double *pdx = new double[tmpGraph.GetWidth()];
	double *pdy = new double[tmpGraph.GetWidth()];
	for(int i=0; i<tmpGraph.GetWidth(); ++i)
	{
		pdx[i]=i;
		pdy[i]=tmpGraph.GetData(i);
	}
	m_curve.setData(pdx,pdy,tmpGraph.GetWidth());
	delete[] pdx;
	delete[] pdy;
	
	
	// Fit dieser Messpunkte
	double dPhase, dFreq, dAmp, dOffs;
	bool bFitValid = tmpGraph.FitSinus(dPhase, dFreq, dAmp, dOffs);
	
	char pcFit[256];
	if(bFitValid)
		sprintf(pcFit, "Fit: y = %.0f * sin(%.4f*x + %.4f) + %.0f", dAmp, dFreq, dPhase, dOffs);
	else 
		sprintf(pcFit, "Fit: invalid!");
	labelFit->setText(pcFit);

	const int FITPUNKTE=16;
	pdx = new double[Config_TofLoader::IMAGES_PER_FOIL*FITPUNKTE];
	pdy = new double[Config_TofLoader::IMAGES_PER_FOIL*FITPUNKTE];
	for(int i=0; i<Config_TofLoader::IMAGES_PER_FOIL*FITPUNKTE; ++i)
	{
		double x = double(i)/double(FITPUNKTE);
		pdx[i] = x;
		pdy[i] = dAmp*sin(x*dFreq + dPhase) + dOffs;
	}
	m_curvefit.setData(pdx,pdy,Config_TofLoader::IMAGES_PER_FOIL*FITPUNKTE);
	delete[] pdx;
	delete[] pdy;
	
	
	// Gesamtkurve
	TmpGraph tmpGraphtotal;
	m_pTofImg->GetTotalGraph(spinBoxROIx1->value(),spinBoxROIx2->value(),spinBoxROIy1->value(),spinBoxROIy2->value(),spinBoxPhase->value(), &tmpGraphtotal);
	pdx = new double[tmpGraphtotal.GetWidth()];
	pdy = new double[tmpGraphtotal.GetWidth()];
	for(int i=0; i<tmpGraphtotal.GetWidth(); ++i)
	{
		pdx[i]=i;
		pdy[i]=tmpGraphtotal.GetData(i);
	}
	m_curvetotal.setData(pdx,pdy,tmpGraphtotal.GetWidth());
	delete[] pdx;
	delete[] pdy;

	
	qwtPlot->replot();
}

void GraphDlg::ROIy1changed(int iVal) { UpdateGraph(); }
void GraphDlg::ROIy2changed(int iVal) { UpdateGraph(); }
void GraphDlg::ROIx1changed(int iVal) { UpdateGraph(); }
void GraphDlg::ROIx2changed(int iVal) { UpdateGraph(); }
void GraphDlg::Foilchanged(int iVal) { UpdateGraph(); }
void GraphDlg::Phasechanged(double dVal) { UpdateGraph(); }

void GraphDlg::Init(int iROIx1, int iROIx2, int iROIy1, int iROIy2, int iFolie)
{
	qwtPlot->setAutoReplot(false);
	qwtPlot->setCanvasBackground(QColor(255,255,255));
	qwtPlot->axisWidget(QwtPlot::xBottom)->setTitle("Time Channels");
	qwtPlot->axisWidget(QwtPlot::yLeft)->setTitle("Counts");
	
	m_pgrid = new QwtPlotGrid;
	m_pgrid->enableXMin(true);
	m_pgrid->enableYMin(true);
	m_pgrid->setMajPen(QPen(Qt::black, 0, Qt::DotLine));
	m_pgrid->setMinPen(QPen(Qt::gray, 0 , Qt::DotLine));
	m_pgrid->attach(qwtPlot);			
	
	spinBoxROIx1->setMinimum(0);
	spinBoxROIx1->setMaximum(Config_TofLoader::IMAGE_WIDTH);
	spinBoxROIx2->setMinimum(0);
	spinBoxROIx2->setMaximum(Config_TofLoader::IMAGE_WIDTH);
	spinBoxROIy1->setMinimum(0);
	spinBoxROIy1->setMaximum(Config_TofLoader::IMAGE_HEIGHT);
	spinBoxROIy2->setMinimum(0);
	spinBoxROIy2->setMaximum(Config_TofLoader::IMAGE_HEIGHT);
	spinBoxFolie->setMinimum(1);
	spinBoxFolie->setMaximum(Config_TofLoader::FOIL_COUNT);
	
	spinBoxROIx1->setValue(iROIx1);
	spinBoxROIx2->setValue(iROIx2);
	spinBoxROIy1->setValue(iROIy1);
	spinBoxROIy2->setValue(iROIy2);
	spinBoxFolie->setValue(iFolie+1);
	
	QwtLegend *m_plegend = new QwtLegend;
	//m_plegend->setItemMode(QwtLegend::CheckableItem);
	qwtPlot->insertLegend(m_plegend, QwtPlot::RightLegend);
	
	QObject::connect(spinBoxROIy1, SIGNAL(valueChanged(int)), this, SLOT(ROIy1changed(int)));
	QObject::connect(spinBoxROIy2, SIGNAL(valueChanged(int)), this, SLOT(ROIy2changed(int)));
	QObject::connect(spinBoxROIx1, SIGNAL(valueChanged(int)), this, SLOT(ROIx1changed(int)));
	QObject::connect(spinBoxROIx2, SIGNAL(valueChanged(int)), this, SLOT(ROIx2changed(int)));
	QObject::connect(spinBoxFolie, SIGNAL(valueChanged(int)), this, SLOT(Foilchanged(int)));
	QObject::connect(spinBoxPhase, SIGNAL(valueChanged(double)), this, SLOT(Phasechanged(double)));			
	
	
	// Kurve für Messpunkte für eine Folie
	QwtSymbol sym;
	sym.setStyle(QwtSymbol::Ellipse);
	sym.setPen(QColor(Qt::blue));
	sym.setBrush(QColor(Qt::blue));
	sym.setSize(5);
	m_curve.setSymbol(sym);
	m_curve.setStyle(QwtPlotCurve::NoCurve);
	m_curve.setRenderHint(QwtPlotItem::RenderAntialiased);
	m_curve.setPen(QPen(Qt::blue));
	m_curve.attach(qwtPlot);
	
	// Kurve für Fits
	m_curvefit.setRenderHint(QwtPlotItem::RenderAntialiased);
	QPen penfit = QPen(Qt::red);
	m_curvefit.setPen(penfit);
	m_curvefit.attach(qwtPlot);
	
	// Gesamtkurve
	m_curvetotal.setRenderHint(QwtPlotItem::RenderAntialiased);
	QPen pentotal = QPen(Qt::black);
	pentotal.setWidth(2);
	m_curvetotal.setPen(pentotal);
	m_curvetotal.attach(qwtPlot);
}

GraphDlg::GraphDlg(QWidget *pParent, TofImage* pTof) : QDialog(pParent), m_pTofImg(pTof), m_curve("Foil"), m_curvefit("Fit"), m_curvetotal("Total"), m_plegend(0), m_pgrid(0)
{
	setupUi(this);
	Init(0, Config_TofLoader::IMAGE_WIDTH-1, 0, Config_TofLoader::IMAGE_HEIGHT-1, 0);
	UpdateGraph();
}

GraphDlg::GraphDlg(QWidget *pParent, TofImage* pTof, int iROIx1, int iROIx2, int iROIy1, int iROIy2, int iFolie) : QDialog(pParent), m_pTofImg(pTof), m_curve("Foil"), m_curvefit("Fit"), m_curvetotal("Total"), m_plegend(0), m_pgrid(0)
{
	setupUi(this);
	Init(iROIx1, iROIx2, iROIy1, iROIy2, iFolie);
	UpdateGraph();
}

GraphDlg::~GraphDlg()
{
	if(m_pgrid) delete m_pgrid;
	if(m_plegend) delete m_plegend;
}
// **************************************************************

// ************************* Server-Dialog ********************************
ServerDlg::ServerDlg(QWidget *pParent) : QDialog(pParent)
{
	setupUi(this);
}

ServerDlg::~ServerDlg()
{
}
// ********************************************************************

// ************************* Server-Dialog ********************************
ServerCfgDlg::ServerCfgDlg(QWidget *pParent) : QDialog(pParent)
{
	setupUi(this);
	QString str; 
	
	str.setNum(s_dLastTime);
	editMeasTime->setText(str);
	
	str.setNum(s_iXRes);
	editxres->setText(str);
	
	str.setNum(s_iYRes);
	edityres->setText(str);

	str.setNum(s_iTRes);
	edittres->setText(str);
}

ServerCfgDlg::~ServerCfgDlg()
{}

double ServerCfgDlg::GetMeasTime()
{
	s_dLastTime = editMeasTime->text().toDouble();
	return s_dLastTime;
}

unsigned int ServerCfgDlg::GetXRes()
{
	s_iXRes = editxres->text().toInt();
	return s_iXRes;
}

unsigned int ServerCfgDlg::GetYRes()
{
	s_iYRes = edityres->text().toInt();
	return s_iYRes;
}

unsigned int ServerCfgDlg::GetTRes()
{
	s_iTRes = edittres->text().toInt();
	return s_iTRes;
}

double ServerCfgDlg::s_dLastTime = 10.0;
unsigned int ServerCfgDlg::s_iXRes = 128;
unsigned int ServerCfgDlg::s_iYRes = 128;
unsigned int ServerCfgDlg::s_iTRes = 128;
// ********************************************************************

#ifdef __CASCADE_QT_CLIENT__
	// Qt-Metaobjekte
	#include "cascadedialogs.moc"
#endif
