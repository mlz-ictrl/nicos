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
// Cascade sub dialogs

#include "cascadedialogs.h"
#include "cascadewidget.h"
#include "helper.h"
#include "logger.h"

#include <stdio.h>
#include <sstream>
#include <QVariant>
#include <QMenu>
#include <QFileDialog>
#include <QDir>


// ************************* Server Command Dialog ********************
CommandDlg::CommandDlg(QWidget *pParent) : QDialog(pParent)
{
	setupUi(this);
}

CommandDlg::~CommandDlg()
{}
// ********************************************************************


// ************************* Kalibrierungs-Dialog *********************
CalibrationDlg::CalibrationDlg(QWidget *pParent, const Bins& bins) :
								QDialog(pParent), m_pgrid(0)
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
// *****************************************************************************




// ************************* Summierungs-Dialog mit Zeitkanälen ****************
void SumDlg::ShowIt()
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	bool *pbChecked = new bool[conf.GetFoilCount()*conf.GetImagesPerFoil()];
	for(int iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
	{
		for(int iKanal=0; iKanal<conf.GetImagesPerFoil(); ++iKanal)
		{
			bool bChecked =
				(m_pTreeItems[iFolie*conf.GetImagesPerFoil() +
				iKanal]->checkState(0)==Qt::Checked);
			pbChecked[iFolie*conf.GetImagesPerFoil() + iKanal] = bChecked;
		}
	}
	emit SumSignal(pbChecked, m_iMode);
	delete[] pbChecked;
}

void SumDlg::SelectAll()
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	for(int iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
	{
		m_pTreeItemsFolien[iFolie]->setCheckState(0,Qt::Checked);
		for(int iKanal=0; iKanal<conf.GetImagesPerFoil(); ++iKanal)
			m_pTreeItems[iFolie*conf.GetImagesPerFoil() + iKanal]
												->setCheckState(0,Qt::Checked);
	}
}

void SumDlg::SelectNone()
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	for(int iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
	{
		m_pTreeItemsFolien[iFolie]->setCheckState(0,Qt::Unchecked);
		for(int iKanal=0; iKanal<conf.GetImagesPerFoil(); ++iKanal)
			m_pTreeItems[iFolie*conf.GetImagesPerFoil() + iKanal]
												->setCheckState(0,Qt::Unchecked);
	}
}

void SumDlg::TreeWidgetClicked(QTreeWidgetItem *item, int column)
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	int iFolie;
	for(iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
		if(m_pTreeItemsFolien[iFolie]==item) break;

	// nicht auf Parent geklickt
	if(iFolie==conf.GetFoilCount()) return;

	for(int iKanal=0; iKanal<conf.GetImagesPerFoil(); ++iKanal)
		m_pTreeItems[iFolie*conf.GetImagesPerFoil() + iKanal]
				->setCheckState(0,m_pTreeItemsFolien[iFolie]->checkState(0));
}

SumDlg::SumDlg(QWidget *pParent) : QDialog(pParent)
{
	setupUi(this);

	const TofConfig& conf = GlobalConfig::GetTofConfig();

	m_pTreeItemsFolien = new QTreeWidgetItem*[conf.GetFoilCount()];
	m_pTreeItems = new QTreeWidgetItem*[conf.GetFoilCount()*
										conf.GetImagesPerFoil()];

	for(int iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
	{
		m_pTreeItemsFolien[iFolie] = new QTreeWidgetItem(treeWidget);
		char pcName[256];
		sprintf(pcName, "Foil %d", iFolie+1);
		m_pTreeItemsFolien[iFolie]->setText(0, pcName);
		m_pTreeItemsFolien[iFolie]->setCheckState(0, Qt::Unchecked);

		for(int iKanal=0; iKanal<conf.GetImagesPerFoil(); ++iKanal)
		{
			m_pTreeItems[iFolie*conf.GetImagesPerFoil() + iKanal] =
								new QTreeWidgetItem(m_pTreeItemsFolien[iFolie]);
			m_pTreeItems[iFolie*conf.GetImagesPerFoil() + iKanal]
											->setCheckState(0, Qt::Unchecked);
			sprintf(pcName, "Time Channel %d", iKanal+1);
			m_pTreeItems[iFolie*conf.GetImagesPerFoil() + iKanal]
														->setText(0, pcName);
		}
	}

	connect(treeWidget, SIGNAL(itemClicked(QTreeWidgetItem *, int)), this,
								SLOT(TreeWidgetClicked(QTreeWidgetItem *, int)));
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
// *****************************************************************************


// ************************* Summierungs-Dialog ohne Zeitkanäle ****************
void SumDlgNoChannels::ShowIt()
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	bool *pbChecked = new bool[conf.GetFoilCount()];
	for(int iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
	{
		bool bChecked = (m_pTreeItemsFolien[iFolie]->checkState(0)==Qt::Checked);
		pbChecked[iFolie] = bChecked;
	}
	emit SumSignal(pbChecked, m_iMode);
	delete[] pbChecked;
}

void SumDlgNoChannels::SelectAll()
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	for(int iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
		m_pTreeItemsFolien[iFolie]->setCheckState(0,Qt::Checked);
}

void SumDlgNoChannels::SelectNone()
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	for(int iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
		m_pTreeItemsFolien[iFolie]->setCheckState(0,Qt::Unchecked);
}

SumDlgNoChannels::SumDlgNoChannels(QWidget *pParent) : QDialog(pParent)
{
	setupUi(this);

	const TofConfig& conf = GlobalConfig::GetTofConfig();

	m_pTreeItemsFolien = new QTreeWidgetItem*[conf.GetFoilCount()];

	for(int iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
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
// *****************************************************************************





// ************************* Zeug für Graph-Dialog *****************************
void GraphDlg::UpdateGraph(void)
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	// Messpunkte für eine Folie
	TmpGraph tmpGraph;
	tmpGraph = m_pTofImg->GetGraph(spinBoxFolie->value()-1);

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
	{
		sprintf(pcFit, "Fit: y = %.0f * sin(%.4f*x + %.4f) + %.0f",
													dAmp, dFreq, dPhase, dOffs);
	}
	else
	{
		sprintf(pcFit, "Fit: invalid!");
		dAmp = dFreq = dPhase = dOffs = 0.;
	}

	labelFit->setText(pcFit);

	const int FITPUNKTE=16;
	pdx = new double[conf.GetImagesPerFoil()*FITPUNKTE];
	pdy = new double[conf.GetImagesPerFoil()*FITPUNKTE];
	for(int i=0; i<conf.GetImagesPerFoil()*FITPUNKTE; ++i)
	{
		double x = double(i)/double(FITPUNKTE);
		pdx[i] = x;
		pdy[i] = dAmp*sin(x*dFreq + dPhase) + dOffs;
	}
	m_curvefit.setData(pdx, pdy, conf.GetImagesPerFoil()*FITPUNKTE);
	delete[] pdx;
	delete[] pdy;

	/*
	// Gesamtkurve
	TmpGraph tmpGraphtotal;
	m_pTofImg->GetTotalGraph(spinBoxROIx1->value(),spinBoxROIx2->value(),
		spinBoxROIy1->value(),spinBoxROIy2->value(),spinBoxPhase->value(),
		&tmpGraphtotal);
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
	*/

	qwtPlot->replot();
}

void GraphDlg::Foilchanged(int iVal)
{
	UpdateGraph();
}

void GraphDlg::Init(int iFolie)
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

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

	spinBoxFolie->setMinimum(1);
	spinBoxFolie->setMaximum(conf.GetFoilCount());
	spinBoxFolie->setValue(iFolie+1);

	QwtLegend *m_plegend = new QwtLegend;
	//m_plegend->setItemMode(QwtLegend::CheckableItem);
	qwtPlot->insertLegend(m_plegend, QwtPlot::RightLegend);

	QObject::connect(spinBoxFolie, SIGNAL(valueChanged(int)), this,
								   SLOT(Foilchanged(int)));

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

GraphDlg::GraphDlg(QWidget *pParent, TofImage* pTof) : QDialog(pParent),
													   m_pTofImg(pTof),
													   m_curve("Foil"),
													   m_curvefit("Fit"),
													   m_curvetotal("Total"),
													   m_plegend(0),
													   m_pgrid(0)
{
	setupUi(this);

	Init(0);
	UpdateGraph();
}

GraphDlg::GraphDlg(QWidget *pParent, TofImage* pTof, int iFolie)
														: QDialog(pParent),
														  m_pTofImg(pTof),
														  m_curve("Foil"),
														  m_curvefit("Fit"),
														  m_curvetotal("Total"),
														  m_plegend(0),
														  m_pgrid(0)
{
	setupUi(this);
	UpdateGraph();
}

GraphDlg::~GraphDlg()
{
	if(m_pgrid) delete m_pgrid;
	if(m_plegend) delete m_plegend;
}
// *****************************************************************************




// ************************* Server-Dialog *************************************
ServerDlg::ServerDlg(QWidget *pParent) : QDialog(pParent)
{
	setupUi(this);
}

ServerDlg::~ServerDlg()
{}

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

	checkBoxPseudoComp->setChecked(s_bUsePseudoComp);

	if(s_iMode==MODE_PAD)
	{
		radioButtonPad->setChecked(1);
		radioButtonTof->setChecked(0);
		toggledmode(0);
	}
	else if(s_iMode==MODE_TOF)
	{
		radioButtonTof->setChecked(1);
		radioButtonPad->setChecked(0);
		toggledmode(1);
	}
	connect(radioButtonTof, SIGNAL(toggled(bool)), this,
							SLOT(toggledmode(bool)));

	setFixedSize(width(),height());
}

ServerCfgDlg::~ServerCfgDlg()
{}

void ServerCfgDlg::toggledmode(bool bChecked)
{
	if(radioButtonTof->isChecked())
	{
		edittres->setEnabled(1);
	}
	else if(radioButtonPad->isChecked())
	{
		edittres->setEnabled(0);
	}
}

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
	if(radioButtonPad->isChecked())
		return 1;

	s_iTRes = edittres->text().toInt();
	return s_iTRes;
}

int ServerCfgDlg::GetMode()
{
	if(radioButtonPad->isChecked())
		s_iMode = MODE_PAD;
	else if(radioButtonTof->isChecked())
		s_iMode = MODE_TOF;
	return s_iMode;
}

bool ServerCfgDlg::GetPseudoComp()
{
	s_bUsePseudoComp = checkBoxPseudoComp->isChecked();
	return s_bUsePseudoComp;
}


void ServerCfgDlg::SetStatXRes(int iXRes) { s_iXRes = iXRes; }
void ServerCfgDlg::SetStatYRes(int iYRes) { s_iYRes = iYRes; }
void ServerCfgDlg::SetStatTRes(int iTRes) { s_iTRes = iTRes; }
void ServerCfgDlg::SetStatMode(int iMode) { s_iMode = iMode; }
void ServerCfgDlg::SetStatTime(double dTime) { s_dLastTime = dTime; }
void ServerCfgDlg::SetStatComp(bool bComp) { s_bUsePseudoComp = bComp; }

int ServerCfgDlg::GetStatXRes() { return s_iXRes; }
int ServerCfgDlg::GetStatYRes() { return s_iYRes; }
int ServerCfgDlg::GetStatTRes() { return s_iTRes; }
int ServerCfgDlg::GetStatMode()  { return s_iMode; }
double ServerCfgDlg::GetStatTime() { return s_dLastTime; }
bool ServerCfgDlg::GetStatComp() { return s_bUsePseudoComp; }


double ServerCfgDlg::s_dLastTime = 10.0;
unsigned int ServerCfgDlg::s_iXRes = 128;
unsigned int ServerCfgDlg::s_iYRes = 128;
unsigned int ServerCfgDlg::s_iTRes = 128;
int ServerCfgDlg::s_iMode = 1;
bool ServerCfgDlg::s_bUsePseudoComp = 0;
// *****************************************************************************



// ************************* Roi-Dlg *******************************************
RoiDlg::RoiDlg(CascadeWidget *pParent) : QDialog(pParent),
										 m_pwidget(pParent), m_pRoi(0)
{
	setupUi(this);

	connect(listRois, SIGNAL(itemSelectionChanged()),
			this, SLOT(ItemSelected()));
	connect(tableParams, SIGNAL(itemChanged(QTableWidgetItem *)),
			this, SLOT(ValueChanged(QTableWidgetItem *)));
	connect(btnDelete, SIGNAL(clicked()), this, SLOT(DeleteItem()));
	connect(btnCopy, SIGNAL(clicked()), this, SLOT(CopyItem()));
	connect(btnFit, SIGNAL(clicked()), this, SLOT(Fit()));


	//--------------------------------------------------------------------------
	QAction *actionNewRect = new QAction("Rectangle", this);
	QAction *actionNewCircle = new QAction("Circle", this);
	QAction *actionNewEllipse = new QAction("Ellipse", this);
	QAction *actionNewCircleRing = new QAction("Circle Ring", this);
	QAction *actionNewCircleSeg = new QAction("Circle Segment", this);

	QMenu *pMenu = new QMenu(this);
	pMenu->addAction(actionNewRect);
	pMenu->addAction(actionNewCircle);
	pMenu->addAction(actionNewEllipse);
	pMenu->addAction(actionNewCircleRing);
	pMenu->addAction(actionNewCircleSeg);

	connect(actionNewRect, SIGNAL(triggered()), this, SLOT(NewRect()));
	connect(actionNewCircle, SIGNAL(triggered()), this, SLOT(NewCircle()));
	connect(actionNewEllipse, SIGNAL(triggered()), this, SLOT(NewEllipse()));
	connect(actionNewCircleRing, SIGNAL(triggered()), this, SLOT(NewCircleRing()));
	connect(actionNewCircleSeg, SIGNAL(triggered()), this, SLOT(NewCircleSeg()));

	btnAdd->setMenu(pMenu);
	//--------------------------------------------------------------------------

	connect(buttonBox, SIGNAL(clicked(QAbstractButton*)),
			m_pwidget, SLOT(RoiDlgAccepted(QAbstractButton*)));
}

RoiDlg::~RoiDlg() { Deinit(); }

// an item (e.g. "circle", "rectangle", ... has been selected)
void RoiDlg::ItemSelected()
{
	if(!m_pRoi) return;

	m_iCurrentItem = listRois->currentRow();

	if(m_iCurrentItem<0 || m_iCurrentItem >= m_pRoi->GetNumElements())
		return;

	RoiElement& elem = m_pRoi->GetElement(m_iCurrentItem);

	tableParams->setRowCount(elem.GetParamCount());
	tableParams->setColumnCount(2);

	for(int iParam=0; iParam<elem.GetParamCount(); ++iParam)
	{
		std::string strParamName = elem.GetParamName(iParam);
		double dParamValue = elem.GetParam(iParam);

		std::ostringstream ostrValue;
		ostrValue << dParamValue;

		QTableWidgetItem *pItemName =
								new QTableWidgetItem(strParamName.c_str());
		pItemName->setFlags(pItemName->flags() & ~Qt::ItemIsEditable);
		tableParams->setItem(iParam, 0, pItemName);

		QTableWidgetItem *pItemValue =
								new QTableWidgetItem(ostrValue.str().c_str());

		pItemValue->setData(Qt::UserRole, iParam);
		pItemValue->setData(Qt::UserRole+1, 1);		// flag 'editable'

		//pItemValue->setData(Qt::UserRole, QVariant::fromValue(pvElem));
		tableParams->setItem(iParam, 1, pItemValue);
	}
}

// a property of the selected item has changed
void RoiDlg::ValueChanged(QTableWidgetItem* pItem)
{
	if(!m_pRoi) return;

	// only edit if this flag is set
	if(pItem->data(Qt::UserRole+1).value<int>() != 1)
		return;

	if(m_iCurrentItem<0 || m_iCurrentItem >= m_pRoi->GetNumElements())
		return;
	RoiElement& elem = m_pRoi->GetElement(m_iCurrentItem);

	QVariant var = pItem->data(Qt::UserRole);
	int iParam = var.value<int>();

	bool bOk = true;
	double dVal = pItem->text().toDouble(&bOk);
	if(!bOk)
	{	// reset to original value
		QString strOldVal;
		strOldVal.setNum(elem.GetParam(iParam));
		pItem->setText(strOldVal);
	}
	else
	{	// accept new value
		elem.SetParam(iParam,dVal);
	}
}

void RoiDlg::CopyItem()
{
	if(!m_pRoi) return;

	if(m_iCurrentItem<0 || m_iCurrentItem >= m_pRoi->GetNumElements())
		return;

	RoiElement& elem = m_pRoi->GetElement(m_iCurrentItem);
	NewElement(elem.copy());
}

void RoiDlg::Fit()
{
	if(!m_pwidget)
		return;

	TmpImage tmpimg;
	if(m_pwidget->IsTofLoaded())
		tmpimg = m_pwidget->GetTof()->GetOverview();
	else
		tmpimg.ConvertPAD(m_pwidget->GetPad());

	double dAmp=0., dCenterX=0., dCenterY=0., dSpreadX=0., dSpreadY=0.;
	bool bOk = tmpimg.FitGaussian(dAmp,dCenterX,dCenterY,dSpreadX,dSpreadY);

	if(bOk)
	{
		std::ostringstream ostr;
		ostr << "amp=" << dAmp << ", x=" << dCenterX << ", y="<<dCenterY
							   << ", sx=" << dSpreadX << ", sy=" << dSpreadY;

		labelFit->setText(ostr.str().c_str());
	}
	else
	{
		labelFit->setText("No valid Gaussian fit found.");
	}
}

void RoiDlg::NewElement(RoiElement* pNewElem)
{
	if(!m_pRoi) return;

	int iPos = m_pRoi->add(pNewElem);
	new QListWidgetItem(m_pRoi->GetElement(iPos).GetName().c_str(), listRois);

	listRois->setCurrentRow(iPos);
	checkBoxUseRoi->setCheckState(Qt::Checked);
}

void RoiDlg::NewCircle() { NewElement(new RoiCircle); }
void RoiDlg::NewEllipse() { NewElement(new RoiEllipse); }
void RoiDlg::NewCircleRing() { NewElement(new RoiCircleRing); }
void RoiDlg::NewCircleSeg() { NewElement(new RoiCircleSegment); }
void RoiDlg::NewRect() { NewElement(new RoiRect); }

void RoiDlg::DeleteItem()
{
	if(!m_pRoi) return;

	if(m_iCurrentItem<0 || m_iCurrentItem >= m_pRoi->GetNumElements())
		return;

	int iCurItem = m_iCurrentItem;

	QListWidgetItem* pItem = listRois->item(iCurItem);
	if(pItem)
	{
		tableParams->setRowCount(0);

		delete pItem;
		m_pRoi->DeleteElement(iCurItem);

		m_iCurrentItem = listRois->currentRow();
	}

	if(m_pRoi->GetNumElements()==0)
		checkBoxUseRoi->setCheckState(Qt::Unchecked);
}

void RoiDlg::ClearList()
{
	listRois->clear();
}

void RoiDlg::SetRoi(const Roi* pRoi)
{
	ClearList();

	if(m_pRoi)
		delete m_pRoi;

	m_pRoi = new Roi(*pRoi);

	// add all roi elements to list
	for(int i=0; i<m_pRoi->GetNumElements(); ++i)
	{
		new QListWidgetItem(m_pRoi->GetElement(i).GetName().c_str(), listRois);
	}

	if(m_pRoi->GetNumElements() > 0)
		listRois->setCurrentRow(0);
}

const Roi* RoiDlg::GetRoi(void) const
{
	return m_pRoi;
}

void RoiDlg::Deinit()
{
	if(m_pRoi)
		delete m_pRoi;
}

// *****************************************************************************





// ******************* Browse Dialog *******************************************

BrowseDlg::BrowseDlg(CascadeWidget *pParent, const char* pcDir)
			: QDialog(pParent), m_pwidget(pParent)
{
	setupUi(this);

	connect(btnBrowse, SIGNAL(clicked()),
			this, SLOT(SelectDir()));
	connect(listFiles, SIGNAL(itemSelectionChanged()),
			this, SLOT(SelectedFile()));

	SetDir(QString(pcDir));
}

BrowseDlg::~BrowseDlg()
{}

void BrowseDlg::SetDir(const QString& strDir)
{
	listFiles->clear();
	labDir->setText(strDir);

	QDir dir(strDir);
	dir.setFilter(QDir::Files | QDir::Hidden);

	QStringList namefilters;
	namefilters << "*.pad" << "*.tof" << "*.PAD" << "*.TOF";
	dir.setNameFilters(namefilters);

	QFileInfoList filelist = dir.entryInfoList();

	for(int iFile=0; iFile<filelist.size(); ++iFile)
	{
		QFileInfo fileinfo = filelist.at(iFile);
		new QListWidgetItem(fileinfo.fileName(), listFiles);
	}
}

void BrowseDlg::SelectDir()
{
	QString strDir = QFileDialog::getExistingDirectory(
				this,
				"Select Directory",
				".",
				QFileDialog::ShowDirsOnly);

	if(strDir == "")
		return;

	SetDir(strDir);
}

void BrowseDlg::SelectedFile()
{
	QListWidgetItem *pCurItem = listFiles->currentItem();
	if(!pCurItem)
		return;

	QString strFile = labDir->text();
	strFile += "/";
	strFile += pCurItem->text();

	m_pwidget->LoadFile(strFile.toAscii().data());
}

// *****************************************************************************





// *********************** Integration Dialog **********************************

IntegrationDlg::IntegrationDlg(CascadeWidget *pParent)
				: QDialog(pParent), m_pwidget(pParent), m_bAutoUpdate(true)
{
	setupUi(this);

	plot->setAutoReplot(false);
	plot->setCanvasBackground(QColor(255,255,255));
	plot->axisWidget(QwtPlot::xBottom)->setTitle("Radius");
	plot->axisWidget(QwtPlot::yLeft)->setTitle("Counts");

	m_pgrid = new QwtPlotGrid;
	m_pgrid->enableXMin(true);
	m_pgrid->enableYMin(true);
	m_pgrid->setMajPen(QPen(Qt::black, 0, Qt::DotLine));
	m_pgrid->setMinPen(QPen(Qt::gray, 0 , Qt::DotLine));
	m_pgrid->attach(plot);

	QwtSymbol sym;
	sym.setStyle(QwtSymbol::Ellipse);
	sym.setPen(QColor(Qt::blue));
	sym.setBrush(QColor(Qt::blue));
	sym.setSize(5);

	m_curve.setRenderHint(QwtPlotItem::RenderAntialiased);
	QPen penfit = QPen(Qt::red);
	m_curve.setPen(penfit);
	m_curve.setSymbol(sym);
	m_curve.attach(plot);

	connect(btnBeamCenter, SIGNAL(clicked()), this, SLOT(UseBeamCenter()));
	connect(btnImageCenter, SIGNAL(clicked()), this, SLOT(UseImageCenter()));
	connect(btnLog10, SIGNAL(toggled(bool)), this, SLOT(SetLog10(bool)));

	connect(doubleSpinBoxX, SIGNAL(valueChanged(double)),
			this, SLOT(UpdateGraph()));
	connect(doubleSpinBoxY, SIGNAL(valueChanged(double)),
			this, SLOT(UpdateGraph()));

	connect(chkAngMean, SIGNAL(stateChanged(int)), this, SLOT(UpdateGraph()));
}

IntegrationDlg::~IntegrationDlg() {}

void IntegrationDlg::UpdateGraph()
{
	if(!m_bAutoUpdate)
		return;

	bool bLog10 = btnLog10->isChecked();
	bool bAngMean = (chkAngMean->checkState()==Qt::Checked);

	TmpImage tmpImg = GetRoiImage();

	const double dRadInc = 1.;
	const double dAngInc = 0.01;

	// TODO: Use beam center!
	Vec2d<double> vecCenter;
	vecCenter[0] = doubleSpinBoxX->value();
	vecCenter[1] = doubleSpinBoxY->value();

	TmpGraph tmpGraph = tmpImg.
					GetRadialIntegration(dAngInc, dRadInc, vecCenter, bAngMean);

	double *pdx = new double[tmpGraph.GetWidth()];
	double *pdy = new double[tmpGraph.GetWidth()];

	double dMax = 1.;
	for(int i=0; i<tmpGraph.GetWidth(); ++i)
		dMax = max(dMax, double(tmpGraph.GetData(i)));

	for(int i=0; i<tmpGraph.GetWidth(); ++i)
	{
		pdx[i] = double(i) * dRadInc;
		pdy[i] = double(tmpGraph.GetData(i)) /* / dMax*/;

		if(bLog10)
			pdy[i] = safe_log10(pdy[i]);
	}
	m_curve.setData(pdx,pdy,tmpGraph.GetWidth());
	delete[] pdx;
	delete[] pdy;

	if(bLog10)
		dMax = safe_log10(dMax);

	plot->setAxisScale(QwtPlot::yLeft, GlobalConfig::GetLogLowerRange(), dMax);
	plot->replot();
}

void IntegrationDlg::UseBeamCenter()
{
	TmpImage tmpImg;

	if(m_pwidget->IsTofLoaded())
		tmpImg = m_pwidget->GetTof()->GetOverview();
	else
		tmpImg.ConvertPAD(m_pwidget->GetPad());

	double dAmp=0., dCenterX=0., dCenterY=0., dSpreadX=0., dSpreadY=0.;
	bool bOk = tmpImg.FitGaussian(dAmp,dCenterX,dCenterY,dSpreadX,dSpreadY);

	if(bOk)
	{
		std::ostringstream ostr;
		ostr << "Gaussian fit with amp=" << dAmp
			 << ", x=" << dCenterX << ", y="<<dCenterY
			 << ", sx=" << dSpreadX << ", sy=" << dSpreadY;

		logger.SetCurLogLevel(LOGLEVEL_INFO);
		logger << "Integration Dialog: " << ostr.str() << "\n";
	}
	else
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Integration Dialog: No valid Gaussian fit found.\n";
	}

	m_bAutoUpdate = false;
	doubleSpinBoxX->setValue(dCenterX);
	doubleSpinBoxY->setValue(dCenterY);
	m_bAutoUpdate = true;

	UpdateGraph();
}

void IntegrationDlg::UseImageCenter()
{
	TmpImage tmpImg = GetRoiImage();

	double dX = double(tmpImg.GetWidth()) * .5;
	double dY = double(tmpImg.GetHeight()) * .5;

	m_bAutoUpdate = false;
	doubleSpinBoxX->setValue(dX);
	doubleSpinBoxY->setValue(dY);
	m_bAutoUpdate = true;

	UpdateGraph();
}

TmpImage IntegrationDlg::GetRoiImage()
{
	TmpImage tmpImg;

	if(m_pwidget->IsPadLoaded())
		tmpImg = m_pwidget->GetPad()->GetRoiImage();
	else if(m_pwidget->IsTofLoaded())
		tmpImg = m_pwidget->GetTof()->GetOverview(true);

	return tmpImg;
}

void IntegrationDlg::SetLog10(bool bLog10)
{
	plot->axisWidget(QwtPlot::yLeft)->setTitle(bLog10?"Counts 10^":"Counts");
	UpdateGraph();
}

// *****************************************************************************






// ************************ Range Dialog ***************************************

RangeDlg::RangeDlg(CascadeWidget *pParent)
		: QDialog(pParent), m_pWidget(pParent), m_bReadOnly(false)
{
	setupUi(this);
	Update();

	connect(btnAuto, SIGNAL(toggled(bool)), this, SLOT(SetAutoRange(bool)));

	connect(spinBoxMin, SIGNAL(valueChanged(double)),
			this, SLOT(RangeChanged()));
	connect(spinBoxMax, SIGNAL(valueChanged(double)),
			this, SLOT(RangeChanged()));
}

RangeDlg::~RangeDlg()
{}

void RangeDlg::SetAutoRange(bool bAuto)
{
	if(m_bReadOnly) return;

	spinBoxMin->setEnabled(!bAuto);
	spinBoxMax->setEnabled(!bAuto);

	bool bAutoRange = btnAuto->isChecked();
	m_pWidget->SetAutoCountRange(bAutoRange);

	if(!bAuto)
		RangeChanged();
}

void RangeDlg::RangeChanged()
{
	if(m_bReadOnly) return;

	btnAuto->setChecked(false);
	double dMin = spinBoxMin->value();
	double dMax = spinBoxMax->value();
	m_pWidget->SetCountRange(dMin, dMax);
}

void RangeDlg::Update()
{
	m_bReadOnly = true;

	QwtDoubleInterval interval = m_pWidget->GetData2d().range();
	spinBoxMin->setValue(interval.minValue());
	spinBoxMax->setValue(interval.maxValue());

	bool bUseAuto = m_pWidget->GetData2d().GetAutoCountRange();
	btnAuto->setChecked(bUseAuto);
	spinBoxMin->setEnabled(!bUseAuto);
	spinBoxMax->setEnabled(!bUseAuto);

	m_bReadOnly = false;
}

void RangeDlg::SetReadOnly(bool bReadOnly)
{ m_bReadOnly = bReadOnly; }

// *****************************************************************************




// ********************* Counts vs Images **************************************

CountsVsImagesDlg::CountsVsImagesDlg(QWidget *pParent)
				 : QDialog(pParent), m_pgrid(0)
{
	setupUi(this);

	listPads->setSelectionMode(QAbstractItemView::ExtendedSelection);

	plot->setAutoReplot(false);
	plot->setCanvasBackground(QColor(255,255,255));
	plot->axisWidget(QwtPlot::xBottom)->setTitle("Images");
	plot->axisWidget(QwtPlot::yLeft)->setTitle("Counts");


	m_pzoomer = new QwtPlotZoomer(plot->canvas());

	m_pzoomer->setSelectionFlags(QwtPicker::RectSelection |
								 QwtPicker::DragSelection);

	m_pzoomer->setMousePattern(QwtEventPattern::MouseSelect2,Qt::RightButton,
							   Qt::ControlModifier);
	m_pzoomer->setMousePattern(QwtEventPattern::MouseSelect3,Qt::RightButton);

	QColor c(Qt::darkBlue);
	m_pzoomer->setRubberBandPen(c);
	m_pzoomer->setTrackerPen(c);


	m_ppanner = new QwtPlotPanner(plot->canvas());
	m_ppanner->setMouseButton(Qt::MidButton);


	m_pgrid = new QwtPlotGrid;
	m_pgrid->enableXMin(true);
	m_pgrid->enableYMin(true);
	m_pgrid->setMajPen(QPen(Qt::black, 0, Qt::DotLine));
	m_pgrid->setMinPen(QPen(Qt::gray, 0 , Qt::DotLine));
	m_pgrid->attach(plot);

	QwtSymbol sym;
	sym.setStyle(QwtSymbol::Ellipse);
	sym.setPen(QColor(Qt::blue));
	sym.setBrush(QColor(Qt::blue));
	sym.setSize(5);

	m_curve.setRenderHint(QwtPlotItem::RenderAntialiased);
	QPen penfit = QPen(Qt::red);
	m_curve.setPen(penfit);
	m_curve.setSymbol(sym);
	m_curve.attach(plot);

	connect(btnAdd, SIGNAL(clicked()), this, SLOT(AddFile()));
	connect(btnDelete, SIGNAL(clicked()), this, SLOT(DeleteFile()));
	connect(btnRoiLoad, SIGNAL(clicked()), this, SLOT(LoadRoi()));
	connect(btnRoiCurrent, SIGNAL(toggled(bool)),
			this, SLOT(SetRoiUseCurrent(bool)));
}

CountsVsImagesDlg::~CountsVsImagesDlg()
{
	if(m_pgrid) delete m_pgrid;
	if(m_pzoomer) delete m_pzoomer;
	if(m_ppanner) delete m_ppanner;
}

void CountsVsImagesDlg::UpdateGraph()
{
	bool bUseRoi = groupRoi->isChecked();
	bool bUseCurRoi = btnRoiCurrent->isChecked();
	QString strRoiFile = editRoi->text();

	const int iPadCnt = listPads->count();

	double *pdx = new double[iPadCnt];
	double *pdy = new double[iPadCnt];

	PadImage pad;
	unsigned int uiMax = 0;
	for(int iItem=0; iItem<iPadCnt; ++iItem)
	{
		QListWidgetItem* pItem = listPads->item(iItem);

		if(!pad.LoadFile(pItem->text().toAscii().data()))
		{
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "CountsDialog: Could not load \""
				   << pItem->text().toAscii().data() << "\".\n";
			continue;
		}

		unsigned int uiCnts = pad.GetCounts();
		uiMax = max(uiMax, uiCnts);

		pdx[iItem] = iItem;
		pdy[iItem] = uiCnts;
	}

	m_curve.setData(pdx, pdy, iPadCnt);

	delete[] pdx;
	delete[] pdy;

	plot->setAxisScale(QwtPlot::yLeft, 0, uiMax);
	plot->setAxisScale(QwtPlot::xBottom, 0, iPadCnt);
	m_pzoomer->setZoomBase();

	plot->replot();
}

void CountsVsImagesDlg::LoadRoi()
{
	QString strFile = QFileDialog::getOpenFileName(this,
							"Open ROI File","",
							"ROI Files (*.roi *.roi);;XML Files (*.xml *.XML);;"
							"All Files (*)");

	editRoi->setText(strFile);
}

void CountsVsImagesDlg::SetRoiUseCurrent(bool bCur)
{
	editRoi->setEnabled(!bCur);
	btnRoiLoad->setEnabled(!bCur);
}

void CountsVsImagesDlg::AddFile()
{
	QStringList pads = QFileDialog::getOpenFileNames(this, "PAD files", "",
							"PAD Files (*.pad *.PAD);;All Files (*)");

	listPads->addItems(pads);
	UpdateGraph();
}

void CountsVsImagesDlg::DeleteFile()
{
	QList<QListWidgetItem*> items = listPads->selectedItems();

	// nothing specific selected -> clear all
	if(items.size() == 0)
		listPads->clear();

	for(int i=0; i<items.size(); ++i)
	{
		if(items[i])
		{
			delete items[i];
			items[i] = 0;
		}
	}

	UpdateGraph();
}
