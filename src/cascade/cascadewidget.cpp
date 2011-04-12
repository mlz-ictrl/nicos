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

#include "cascadewidget.h"

#include <qapplication.h>
#include <qmainwindow.h>
#include <qtoolbar.h>
#include <qtoolbutton.h>
#include <qprinter.h>
#include <qprintdialog.h>
#include <qpen.h>
#include <QtCore/QVariant>
#include <QtCore/QTimer>
#include <QtGui/QGridLayout>
#include <QtGui/QMenu>
#include <QtGui/QMenuBar>
#include <QtGui/QStatusBar>
#include <QtGui/QGroupBox>
#include <QtGui/QFileDialog>
#include <QtGui/QSlider>
#include <QtGui/QLabel>
#include <QtGui/QPainter>
#include <QDialog>
#include <QLine>
#include <QMessageBox>

#include <iostream>

#include "tofloader.h"
#include "tofdata.h"
#include "cascadedialogs.h"
#include "bins.h"


static inline long GetFileSize(const char* pcFileName)
{
	FILE* pf = fopen(pcFileName, "rb");
	if(!pf) return 0;
	
	fseek(pf, 0, SEEK_END);
	long lSize = ftell(pf);
	fseek(pf, 0, SEEK_SET);
	
	fclose(pf);
	return lSize;
}


MainZoomer::MainZoomer(QwtPlotCanvas *canvas, const QwtPlotSpectrogram* pData) : QwtPlotZoomer(canvas), m_pData(pData)
{
	setTrackerMode(AlwaysOn);
	setSelectionFlags(QwtPicker::RectSelection | QwtPicker::DragSelection);
}

QwtText MainZoomer::trackerText(const QwtDoublePoint &pos) const
{
	char pcStr[256];
	sprintf(pcStr, "Pixel: %d, %d", int(pos.x()), int(pos.y()));
	QString str = pcStr;
	
	const MainRasterData& rasterdata = (const MainRasterData&)m_pData->data();
	
	//double dVal = rasterdata.value(pos.x(),pos.y());
	double dVal = rasterdata.GetValueRaw(pos.x(),pos.y());
	
	str += QString("\nValue: ");
	//if(dVal>-std::numeric_limits<double>::max())	// falls gültiger Wert
	{
		//if(rasterdata.GetLog10()) str+=QString("10^");
		sprintf(pcStr, "%.4g", dVal);
		str += QString(pcStr);
	}
	//else
	//	str += QString("0");

	QwtText text = str;
	QColor bg(Qt::white);
	bg.setAlpha(200);
	text.setBackgroundBrush(QBrush(bg));
	return text;
}

/////////////////////////////////////////////////////////////////////////////////////

Plot::Plot(QWidget *parent): QwtPlot(parent), m_pSpectrogram(0), m_pZoomer(0)
{
	InitPlot();
}

Plot::~Plot()
{
	DeinitPlot();
}

void Plot::InitPlot()
{
	DeinitPlot();
	
	axisWidget(QwtPlot::xBottom)->setTitle("x Pixels");
	axisWidget(QwtPlot::yLeft)->setTitle("y Pixels");
	
	m_pSpectrogram = new QwtPlotSpectrogram();
	m_pSpectrogram->setData(PadData());	// Dummy-Objekt
	m_pSpectrogram->attach(this);
	setCanvasBackground(QColor(255,255,255));
	SetColorMap(false);

	QwtScaleWidget *rightAxis = axisWidget(QwtPlot::yRight);
	rightAxis->setColorBarEnabled(true);
	rightAxis->setColorMap(m_pSpectrogram->data().range(),m_pSpectrogram->colorMap());

	setAxisScale(QwtPlot::yLeft,0,Config_TofLoader::GetImageHeight());
	setAxisScale(QwtPlot::xBottom,0,Config_TofLoader::GetImageWidth());
	setAxisScale(QwtPlot::yRight,m_pSpectrogram->data().range().minValue(),m_pSpectrogram->data().range().maxValue());
	enableAxis(QwtPlot::yRight);

	plotLayout()->setAlignCanvasToScales(true);

	m_pZoomer = new MainZoomer(canvas(), m_pSpectrogram);
	m_pZoomer->setMousePattern(QwtEventPattern::MouseSelect2,Qt::RightButton, Qt::ControlModifier);
	m_pZoomer->setMousePattern(QwtEventPattern::MouseSelect3,Qt::RightButton);

	QwtPlotPanner *panner = new QwtPlotPanner(canvas());
	panner->setAxisEnabled(QwtPlot::yRight, false);
	panner->setMouseButton(Qt::MidButton);

	QFontMetrics fm(axisWidget(QwtPlot::yLeft)->font());
	axisScaleDraw(QwtPlot::yLeft)->setMinimumExtent(fm.width("100."));

	QColor c(Qt::darkBlue);
	m_pZoomer->setRubberBandPen(c);
	m_pZoomer->setTrackerPen(c);
}

void Plot::DeinitPlot()
{
}

void Plot::ChangeRange()
{
	setAxisScale(QwtPlot::yRight, m_pSpectrogram->data().range().minValue(), m_pSpectrogram->data().range().maxValue());
	axisWidget(QwtPlot::yRight)->setColorMap(m_pSpectrogram->data().range(), m_pSpectrogram->colorMap());

	QwtValueList contourLevels;
	for(double level=0.5; level<10.0; level+=1.0)
		contourLevels += level;
	m_pSpectrogram->setContourLevels(contourLevels);
}

QwtPlotZoomer* Plot::GetZoomer()
{ 
	return m_pZoomer;
}

void Plot::SetData(QwtRasterData* pData)
{
	if(!pData) return;
	m_pSpectrogram->setData(*pData);
	ChangeRange();
}

const QwtRasterData* Plot::GetData() const
{
	return &m_pSpectrogram->data();
}

void Plot::SetColorMap(bool bCyclic)
{
	if(m_pSpectrogram==NULL) return;
	
	if(bCyclic)	// Für Phasen
	{
		QwtLinearColorMap colorMap(Qt::blue, Qt::blue);
		colorMap.addColorStop(0.0, Qt::blue);
		colorMap.addColorStop(0.75, Qt::red);
		colorMap.addColorStop(0.5, Qt::yellow);
		colorMap.addColorStop(0.25, Qt::cyan);
		colorMap.addColorStop(1.0, Qt::blue);
		m_pSpectrogram->setColorMap(colorMap);
	}
	else
	{
		QwtLinearColorMap colorMap(Qt::blue, Qt::red);
		colorMap.addColorStop(0.0, Qt::blue);
		colorMap.addColorStop(0.33, Qt::cyan);
		colorMap.addColorStop(0.66, Qt::yellow);
		colorMap.addColorStop(1.0, Qt::red);
		m_pSpectrogram->setColorMap(colorMap);
	}
}

void Plot::showContour(bool on)
{
	m_pSpectrogram->setDisplayMode(QwtPlotSpectrogram::ContourMode, on);
	replot();
}

void Plot::showSpectrogram(bool on)
{
	m_pSpectrogram->setDisplayMode(QwtPlotSpectrogram::ImageMode, on);
	m_pSpectrogram->setDefaultContourPen(on ? QPen() : QPen(Qt::NoPen));
	replot();
}

void Plot::printPlot()
{
	QPrinter printer;
	printer.setOrientation(QPrinter::Landscape);
	QPrintDialog dialog(&printer);
	if(dialog.exec()) print(printer);
}


/////////////////////////////////////////////////////////////////////////////////////

CascadeWidget::CascadeWidget(QWidget *pParent) : QWidget(pParent), m_bForceReinit(0), m_pPad(0),m_pTof(0),m_pdata2d(0), m_iMode(MODE_SLIDES), m_iFolie(0), m_iZeitkanal(0), m_bLog(0), m_bSpectrogram(1), m_bContour(0)
{
	m_pPlot = new Plot(this);

	QGridLayout *gridLayout = new QGridLayout(this);
	gridLayout->addWidget(m_pPlot,0,0,1,1);
	this->setLayout(gridLayout);
	
	UpdateLabels();
}

CascadeWidget::~CascadeWidget()
{
	Unload();
}

TofImage* CascadeWidget::GetTof() { return m_pTof; }
PadData* CascadeWidget::GetPad() { return m_pPad; }
Data2D* CascadeWidget::GetData2d() { return m_pdata2d; }
Plot* CascadeWidget::GetPlot() { return m_pPlot; }

void CascadeWidget::Unload()
{
	if(m_pPad) { delete m_pPad; m_pPad=NULL; }
	if(m_pTof) { delete m_pTof; m_pTof=NULL; }
	if(m_pdata2d)
	{ 
		m_pdata2d->clearData();
		delete m_pdata2d; m_pdata2d=NULL;
	}
}

void* CascadeWidget::NewPad()
{
	// Tof geladen?
	if(!m_pPad || m_pTof || m_pdata2d || m_bForceReinit)
	{
		Unload();
		m_pPad = new PadData();
		m_pPad->SetLog10(m_bLog);
		//m_pPlot->SetData(m_pPad);
		
		//m_pPlot->InitPlot();
		m_bForceReinit=false;
	}
	// ansonsten einfach bestehendes PAD-Objekt recyclen
	
	//return ((PadData*)m_pPlot->GetData())->GetRawData();
	return m_pPad->GetRawData();
}

void* CascadeWidget::NewTof()
{
	// Pad geladen?
	if(m_pPad || !m_pTof || !m_pdata2d || m_bForceReinit)
	{
		Unload();
		m_pTof = new TofImage;
		m_pdata2d = new Data2D;	
		m_pdata2d->SetLog10(m_bLog);
		//m_pPlot->SetData(m_pdata2d);
		
		//m_pPlot->InitPlot();
		m_bForceReinit=false;
	}
	// ansonsten einfach bestehendes TOF-Objekt recyclen
	
	return m_pTof->GetRawData();
}

unsigned int* CascadeWidget::GetRawData()
{
	if(IsTofLoaded())
		return m_pTof->GetRawData();
	else if(IsPadLoaded())
		return m_pPad->GetRawData();
	return 0;
}

bool CascadeWidget::LoadPadFile(const char* pcFile)
{
	NewPad();
	int iRet = m_pPad->LoadFile(pcFile);
	if(iRet == LOAD_SIZE_MISMATCH)
	{
		long lSize = GetFileSize(pcFile);
		if(Config_TofLoader::GuessConfigFromSize(int(lSize)/4, false))
		{
			m_bForceReinit = true;
			NewPad();
			iRet = m_pPad->LoadFile(pcFile);
		}
	}
	if(iRet) UpdateGraph();
	return iRet;
}

bool CascadeWidget::LoadTofFile(const char* pcFile)
{
	NewTof();
	int iRet = m_pTof->LoadFile(pcFile);
	
	if(iRet == LOAD_SIZE_MISMATCH)
	{
		long lSize = GetFileSize(pcFile);
		if(Config_TofLoader::GuessConfigFromSize(int(lSize)/4, true))
		{
			m_bForceReinit = true;
			NewTof();
			iRet = m_pTof->LoadFile(pcFile);
		}
	}	
	
	if(iRet) viewOverview();
	return iRet;
}

bool CascadeWidget::LoadPadMem(const char* pcMem, unsigned int uiLen)
{
	NewPad();
	int iRet = m_pPad->LoadMem((unsigned int*)pcMem, uiLen/4);
	
	if(iRet == LOAD_SIZE_MISMATCH)
	{
		if(Config_TofLoader::GuessConfigFromSize(uiLen/4, false))
		{
			m_bForceReinit = true;
			NewPad();
			iRet = m_pPad->LoadMem((unsigned int*)pcMem, uiLen/4);
		}
	}	
	
	if(iRet) UpdateGraph();
	return iRet;
}

bool CascadeWidget::LoadTofMem(const char* pcMem, unsigned int uiLen)
{
	NewTof();
	int iRet = m_pTof->LoadMem((unsigned int*)pcMem, uiLen/4);
	
	if(iRet == LOAD_SIZE_MISMATCH)
	{
		if(Config_TofLoader::GuessConfigFromSize(uiLen/4, true))
		{
			m_bForceReinit = true;
			NewTof();
			iRet = m_pTof->LoadMem((unsigned int*)pcMem, uiLen/4);
		}
	}	
	
	if(iRet) viewOverview();
	return iRet;
}

bool CascadeWidget::IsTofLoaded() const
{
	return bool(m_pTof) && bool(m_pdata2d);
}

bool CascadeWidget::IsPadLoaded() const
{
	return bool(m_pPad);
}

void CascadeWidget::UpdateLabels()
{
	if(m_pTof)
	{
		switch(m_iMode)
		{
			case MODE_SLIDES:
			case MODE_SUMS:
				m_pPlot->axisWidget(QwtPlot::yRight)->setTitle(m_bLog?"Counts 10^":"Counts");
				break;

			case MODE_PHASES:
			case MODE_PHASESUMS:
				m_pPlot->axisWidget(QwtPlot::yRight)->setTitle(m_bLog?"Phase [DEG] 10^":"Phase [DEG]");
				break;

			case MODE_CONTRASTS:
			case MODE_CONTRASTSUMS:
				m_pPlot->axisWidget(QwtPlot::yRight)->setTitle(m_bLog?"Contrast 10^":"Contrast");
				break;
		}
	}
	else/* if(m_pPad)*/
	{
		m_pPlot->axisWidget(QwtPlot::yRight)->setTitle(m_bLog?"Counts 10^":"Counts");
	}	
}

void CascadeWidget::UpdateGraph()
{
	if(IsPadLoaded())
	{
		//m_pPad->UpdateRange();
		m_pPlot->SetData(m_pPad);	// !!
	}
	else if(IsTofLoaded())
	{
		if(m_iMode==MODE_SLIDES)
		{
			m_pdata2d->clearData();
			m_pTof->GetROI(0,Config_TofLoader::GetImageWidth()-1,0,Config_TofLoader::GetImageHeight()-1,m_iFolie,m_iZeitkanal,m_pdata2d);
		}
		else if(m_iMode==MODE_PHASES)
		{
			m_pdata2d->clearData();
			m_pTof->GetPhaseGraph(m_iFolie, m_pdata2d);
		}
		else if(m_iMode==MODE_CONTRASTS)
		{
			m_pdata2d->clearData();
			m_pTof->GetContrastGraph(m_iFolie, m_pdata2d);
		}

		m_pdata2d->UpdateRange();
		m_pPlot->SetData(m_pdata2d);	// !!
	}
	
	if(IsPadLoaded() || IsTofLoaded())
	{
		m_pPlot->showSpectrogram(m_bSpectrogram);
		m_pPlot->showContour(m_bContour);
		//m_pPlot->replot();		// !!
	}
	UpdateLabels();
}

int CascadeWidget::GetMode() { return m_iMode; }
void CascadeWidget::SetMode(int iMode) { m_iMode = iMode; }

int CascadeWidget::GetFoil() const { return m_iFolie; }
void CascadeWidget::SetFoil(int iFolie) { m_iFolie = iFolie; }

int CascadeWidget::GetTimechannel() const { return m_iZeitkanal; }
void CascadeWidget::SetTimechannel(int iKanal) { m_iZeitkanal = iKanal; }

bool CascadeWidget::GetLog10() { return m_bLog; }
void CascadeWidget::SetLog10(bool bLog10)
{ 
	m_bLog = bLog10;
	if(m_pPad)
	{
		m_pPad->SetLog10(bLog10);
		m_pPlot->ChangeRange();
	}
	else if(m_pdata2d)
	{
		m_pdata2d->SetLog10(bLog10);
		m_pPlot->ChangeRange();
	}
	UpdateGraph();
}

void CascadeWidget::SetSpectrogram(bool bSpect)
{
	m_bSpectrogram = bSpect;
	GetPlot()->showSpectrogram(bSpect);
}

void CascadeWidget::SetContour(bool bCont)
{
	m_bContour = bCont;
	GetPlot()->showContour(bCont);
}

void CascadeWidget::UpdateRange()
{
	if(IsTofLoaded())
		GetData2d()->UpdateRange();
	else if(IsPadLoaded())
		GetPad()->UpdateRange();
}

void CascadeWidget::viewOverview()
{
	if(!IsTofLoaded()) return;
	SetMode(MODE_SUMS);
	
	GetData2d()->clearData();
	GetTof()->GetOverview(GetData2d());
	GetData2d()->SetPhaseData(false);
	GetPlot()->SetColorMap(false);
	
	UpdateGraph();
}

void CascadeWidget::viewSlides()
{
	if(!IsTofLoaded()) return;
	SetMode(MODE_SLIDES);
	
	GetData2d()->SetPhaseData(false);
	GetPlot()->SetColorMap(false);
	
	UpdateGraph();
}

void CascadeWidget::viewPhases()
{
	if(!IsTofLoaded()) return;
	SetMode(MODE_PHASES);
	
	GetData2d()->SetPhaseData(true);
	GetPlot()->SetColorMap(true);
	
	UpdateGraph();
}

void CascadeWidget::viewContrasts()
{
	if(!IsTofLoaded()) return;
	SetMode(MODE_CONTRASTS);
	
	GetData2d()->SetPhaseData(false);
	GetPlot()->SetColorMap(false);
	
	UpdateGraph();
}

void CascadeWidget::viewFoilSums(const bool* pbKanaele)
{
	SetMode(MODE_SUMS);
	GetTof()->AddFoils(pbKanaele, GetData2d());
	
	UpdateRange();
	UpdateGraph();
}

void CascadeWidget::viewPhaseSums(const bool* pbFolien)
{
	SetMode(MODE_PHASESUMS);
	GetTof()->AddPhases(pbFolien, GetData2d());
	
	UpdateRange();
	UpdateGraph();
}

void CascadeWidget::viewContrastSums(const bool* pbFolien)
{
	SetMode(MODE_CONTRASTSUMS);
	GetTof()->AddContrasts(pbFolien, GetData2d());
	
	UpdateRange();
	UpdateGraph();
}

void CascadeWidget::showCalibrationDlg(int iNumBins)
{
	if(!IsTofLoaded()) return;
	Bins bins(iNumBins, 0., 360.);
	
	QwtDoubleRect rect = GetPlot()->GetZoomer()->zoomRect();
	int iROIx1 = rect.left(),
	iROIx2 = rect.right(),
	iROIy1 = rect.top(),
	iROIy2 = rect.bottom();
	
	TmpImage tmpimg[4];
	for(int iFolie=0; iFolie<Config_TofLoader::GetFoilCount(); ++iFolie)
		GetTof()->GetPhaseGraph(iFolie, &tmpimg[iFolie], iROIx1, iROIx2, iROIy1, iROIy2, true);
	
	int iW = iROIx2-iROIx1; if(iW<0) iW=-iW;
	int iH = iROIy2-iROIy1; if(iH<0) iH=-iH;
	
	for(int iFolie=/*1*/0; iFolie<Config_TofLoader::GetFoilCount(); ++iFolie)
		for(int iY=0; iY<iH; ++iY)
			for(int iX=0; iX<iW; ++iX)
			{
				double dVal = tmpimg[iFolie].GetData(iX,iY)/* - tmpimg[0].GetData(iX,iY)*/;
				if(dVal==0.) continue;
				bins.Inc(dVal);
			}		
	
	CalibrationDlg CalDlg(this, bins);
	CalDlg.exec();
}

void CascadeWidget::showGraphDlg()
{
	if(!IsTofLoaded()) return;
	
	QwtDoubleRect rect = GetPlot()->GetZoomer()->zoomRect();
	int iROIx1 = rect.left(),
	iROIx2 = rect.right(),
	iROIy1 = rect.top(),
	iROIy2 = rect.bottom();
	
	GraphDlg graphdlg(this, GetTof(), iROIx1, iROIx2, iROIy1, iROIy2, m_iFolie);
	graphdlg.exec();
}

void CascadeWidget::SumDlgSlot(const bool *pbKanaele, int iMode)
{
	switch(iMode)
	{
		case MODE_SLIDES:
		case MODE_SUMS:
			viewFoilSums(pbKanaele);
			break;
			
		case MODE_PHASES:
		case MODE_PHASESUMS:
			viewPhaseSums(pbKanaele);
			break;
			
		case MODE_CONTRASTS:
		case MODE_CONTRASTSUMS:
			viewContrastSums(pbKanaele);
			break;
	}
	UpdateLabels();
	emit SumDlgSignal(pbKanaele, iMode);
}

void CascadeWidget::showSumDlg()
{
	if(!IsTofLoaded()) return;

	static SumDlg *pSummenDlgSlides = NULL;
	static SumDlgNoChannels *pSummenDlgPhases = NULL;
	static SumDlgNoChannels *pSummenDlgContrasts = NULL;

	switch(GetMode())
	{
		case MODE_SLIDES:
		case MODE_SUMS:
			if(!pSummenDlgSlides) pSummenDlgSlides = new SumDlg(this);
			connect(pSummenDlgSlides, SIGNAL(SumSignal(const bool *, int)), this, SLOT(SumDlgSlot(const bool *, int)));
			
			pSummenDlgSlides->SetMode(GetMode());
			pSummenDlgSlides->show();
			pSummenDlgSlides->raise();
			pSummenDlgSlides->activateWindow();
			break;
			
		case MODE_PHASES:
		case MODE_PHASESUMS:
			if(!pSummenDlgPhases) pSummenDlgPhases = new SumDlgNoChannels(this);
			connect(pSummenDlgPhases, SIGNAL(SumSignal(const bool *, int)), this, SLOT(SumDlgSlot(const bool *, int)));
			
			pSummenDlgPhases->SetMode(GetMode());
			pSummenDlgPhases->show();
			pSummenDlgPhases->raise();
			pSummenDlgPhases->activateWindow();
			break;
			
		case MODE_CONTRASTS:
		case MODE_CONTRASTSUMS:
			if(!pSummenDlgContrasts) pSummenDlgContrasts = new SumDlgNoChannels(this);
			connect(pSummenDlgContrasts, SIGNAL(SumSignal(const bool *, int)), this, SLOT(SumDlgSlot(const bool *, int)));
			
			pSummenDlgContrasts->SetMode(GetMode());
			pSummenDlgContrasts->show();
			pSummenDlgContrasts->raise();
			pSummenDlgContrasts->activateWindow();
			break;
	}	
}
