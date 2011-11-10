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
// Plotter initially based on "spectrogram" qwt sample code

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
#include "helper.h"
#include "logger.h"


//------------------------------------------------------------------------------
// picker

MainPicker::MainPicker(QwtPlotCanvas* pcanvas)
		   : QwtPlotPicker(pcanvas),
			 m_iRoiDrawMode(ROI_DRAW_RECT), m_pCurRoi(0)
{
	setSelectionFlags(QwtPicker::RectSelection | QwtPicker::DragSelection);

	QColor c(Qt::darkBlue);
	setRubberBandPen(c);
	setTrackerPen(c);

	setRubberBand(RectRubberBand);
	setTrackerMode(QwtPicker::ActiveOnly);

	connect((QwtPlotPicker*)this, SIGNAL(selected (const QwtDoubleRect&)),
			this, SLOT(selectedRect (const QwtDoubleRect&)));
}

MainPicker::~MainPicker()
{}

QwtText MainPicker::trackerText(const QwtDoublePoint &pos) const
{
	QString str;
	switch(m_iRoiDrawMode)
	{
		case ROI_DRAW_RECT:
			str += "Drawing Rectangle";
			break;
		case ROI_DRAW_CIRC:
			str += "Drawing Circle";
			break;
		case ROI_DRAW_CIRCRING:
			str += "Drawing Circle Ring";
			break;
		case ROI_DRAW_CIRCSEG:
			str += "Drawing Circle Segment";
			break;
		case ROI_DRAW_ELLIPSE:
			str += "Drawing Ellipse";
			break;
	}

	str += "\nPixel: ";
	str += QString::number(int(pos.x()));
	str += ", ";
	str += QString::number(int(pos.y()));

	QwtText text = str;
	QColor bg(Qt::white);
	bg.setAlpha(200);
	text.setBackgroundBrush(QBrush(bg));
	return text;
}

void MainPicker::SetRoiDrawMode(int iMode)
{
	m_iRoiDrawMode = iMode;

	switch(iMode)
	{
		case ROI_DRAW_RECT:
			setRubberBand(RectRubberBand);
			break;
		case ROI_DRAW_CIRC:
			setRubberBand(EllipseRubberBand);	// !!
			break;
		case ROI_DRAW_CIRCRING:
			setRubberBand(EllipseRubberBand);	// !!
			break;
		case ROI_DRAW_CIRCSEG:
			setRubberBand(EllipseRubberBand);	// !!
			break;
		case ROI_DRAW_ELLIPSE:
			setRubberBand(EllipseRubberBand);
			break;
	}
}

void MainPicker::selectedRect(const QwtDoubleRect &rect)
{
	if(m_pCurRoi == NULL)
		return;

	Vec2d<int> bottomleft;
	Vec2d<int> topright;

	bottomleft[0] = rect.bottomLeft().x();
	bottomleft[1] = rect.bottomLeft().y();
	topright[0] = rect.topRight().x();
	topright[1] = rect.topRight().y();

	RoiElement* pElem = 0;

	switch(m_iRoiDrawMode)
	{
		case ROI_DRAW_RECT:
		{
			pElem = new RoiRect(bottomleft, topright);
			break;
		}

		case ROI_DRAW_CIRC:
		{
			double dRadius = double(topright[0] - bottomleft[0]) * 0.5;
			Vec2d<double> vecCenter = (topright.cast<double>()-
									  bottomleft.cast<double>()) * 0.5 +
									  bottomleft.cast<double>();

			pElem = new RoiCircle(vecCenter, dRadius);
			break;
		}

		case ROI_DRAW_CIRCRING:
		{
			double dRadius = double(topright[0] - bottomleft[0]) * 0.5;
			Vec2d<double> vecCenter = (topright.cast<double>()-
									  bottomleft.cast<double>()) * 0.5 +
									  bottomleft.cast<double>();

			pElem = new RoiCircleRing(vecCenter, dRadius-5., dRadius+5.);
			break;
		}

		case ROI_DRAW_CIRCSEG:
		{
			break;
		}

		case ROI_DRAW_ELLIPSE:
		{
			double dRadiusX = double(topright[0] - bottomleft[0]) * 0.5;
			double dRadiusY = double(topright[1] - bottomleft[1]) * 0.5;
			Vec2d<double> vecCenter = (topright.cast<double>()-
									  bottomleft.cast<double>()) * 0.5 +
									  bottomleft.cast<double>();

			pElem = new RoiEllipse(vecCenter, dRadiusX, dRadiusY);
			break;
		}
	}

	if(pElem)
	{
		m_pCurRoi->add(pElem);
		emit RoiHasChanged();
	}
}

int MainPicker::GetRoiDrawMode() const { return m_iRoiDrawMode; }
void MainPicker::SetCurRoi(Roi* pRoi) { m_pCurRoi = pRoi; }



//------------------------------------------------------------------------------
// zoomer

MainZoomer::MainZoomer(QwtPlotCanvas *canvas, const QwtPlotSpectrogram* pData)
										: QwtPlotZoomer(canvas), m_pData(pData)
{
	setSelectionFlags(QwtPicker::RectSelection | QwtPicker::DragSelection);

	setMousePattern(QwtEventPattern::MouseSelect2,Qt::RightButton,
													Qt::ControlModifier);
	setMousePattern(QwtEventPattern::MouseSelect3,Qt::RightButton);

	QColor c(Qt::darkBlue);
	setRubberBandPen(c);
	setTrackerPen(c);

	setTrackerMode(AlwaysOn);
}

MainZoomer::~MainZoomer()
{}

QwtText MainZoomer::trackerText(const QwtDoublePoint &pos) const
{
	QString str = "Pixel: ";
	str += QString::number(int(pos.x()));
	str += ", ";
	str += QString::number(int(pos.y()));

	const MainRasterData& rasterdata = (const MainRasterData&)m_pData->data();

	str += "\nValue: ";
	str += QString::number(rasterdata.GetValueRaw(pos.x(),pos.y()));

	QwtText text = str;
	QColor bg(Qt::white);
	bg.setAlpha(200);
	text.setBackgroundBrush(QBrush(bg));
	return text;
}



//------------------------------------------------------------------------------
// panner

MainPanner::MainPanner(QwtPlotCanvas *canvas) : QwtPlotPanner(canvas)
{
	setAxisEnabled(QwtPlot::yRight, false);
	setMouseButton(Qt::MidButton);
}

MainPanner::~MainPanner()
{}




//------------------------------------------------------------------------------
// plot

Plot::Plot(QWidget *parent) : QwtPlot(parent), m_pSpectrogram(0),
							  m_pZoomer(0), m_pPanner(0), m_pRoiPicker(0),
							  m_pImage(0)
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
	m_pSpectrogram->setData(Data2D());		// Dummy-Objekt
	m_pSpectrogram->setDisplayMode(QwtPlotSpectrogram::ImageMode, true);
	m_pSpectrogram->setDisplayMode(QwtPlotSpectrogram::ContourMode, false);
	m_pSpectrogram->attach(this);

	setCanvasBackground(QColor(255,255,255));
	SetColorMap(false);

	enableAxis(QwtPlot::yRight);
	axisWidget(QwtPlot::yRight)->setColorBarEnabled(true);

	ChangeRange();
	ChangeRange_xy();

	plotLayout()->setAlignCanvasToScales(true);

	m_pZoomer = new MainZoomer(canvas(), m_pSpectrogram);
	m_pPanner = new MainPanner(canvas());

	m_pRoiPicker = new MainPicker(canvas());
	m_pRoiPicker->setEnabled(false);

	// avoid jumping of the layout
	axisScaleDraw(QwtPlot::yLeft)->setMinimumExtent(35);
	axisScaleDraw(QwtPlot::yRight)->setMinimumExtent(55);
	axisWidget(QwtPlot::yRight)->setMinBorderDist(25,0);
}

/*
void Plot::ChangeLog(bool bLog10)
{
	if(bLog10)
		axisScaleDraw(QwtPlot::yRight)->setMinimumExtent(50);
	else
		axisScaleDraw(QwtPlot::yRight)->setMinimumExtent(75);
}
*/

void Plot::DeinitPlot()
{
	m_pImage = 0;
	if(m_pZoomer) { delete m_pZoomer; m_pZoomer=0; }
	if(m_pPanner) { delete m_pPanner; m_pPanner=0; }
	if(m_pRoiPicker) { delete m_pRoiPicker; m_pRoiPicker=0; }
	if(m_pSpectrogram) { delete m_pSpectrogram; m_pSpectrogram=0; }
}

void Plot::ChangeRange()
{
	setAxisScale(QwtPlot::yRight, m_pSpectrogram->data().range().minValue(),
								m_pSpectrogram->data().range().maxValue());
	axisWidget(QwtPlot::yRight)->setColorMap(m_pSpectrogram->data().range(),
								m_pSpectrogram->colorMap());
}

void Plot::ChangeRange_xy()
{
	if(m_pImage)
	{
		// use dimensions of image

		setAxisScale(QwtPlot::yLeft, 0, m_pImage->GetHeight());
		setAxisScale(QwtPlot::xBottom, 0, m_pImage->GetWidth());
	}
	else
	{
		// otherwise: global config

		const PadConfig& conf = GlobalConfig::GetTofConfig();
		setAxisScale(QwtPlot::yLeft, 0, conf.GetImageHeight());
		setAxisScale(QwtPlot::xBottom, 0, conf.GetImageWidth());
	}

	if(m_pZoomer)
		m_pZoomer->setZoomBase();
}

QwtPlotZoomer* Plot::GetZoomer() { return m_pZoomer; }
QwtPlotPanner* Plot::GetPanner() { return m_pPanner; }
QwtPlotPicker* Plot::GetRoiPicker() { return m_pRoiPicker; }

const QwtRasterData* Plot::GetData() const
{
	return &m_pSpectrogram->data();
}

void Plot::SetData(Data2D* pData, bool bUpdate)
{
	m_pImage = pData->GetImage();

	if(bUpdate)
	{
		m_pSpectrogram->setData(*pData);
		ChangeRange();
	}
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

void Plot::printPlot()
{
	QPrinter printer;
	printer.setOrientation(QPrinter::Landscape);
	QPrintDialog dialog(&printer);
	if(dialog.exec())
		print(printer);
}

void Plot::replot()
{
	QwtPlot::replot();
}




//------------------------------------------------------------------------------
// widget

CascadeWidget::CascadeWidget(QWidget *pParent) : QWidget(pParent),
												 m_bForceReinit(0),
												 m_pPad(0),
												 m_pTof(0),
												 m_pTmpImg(0),
												 m_iMode(MODE_SLIDES),
												 m_iFolie(0),
												 m_iZeitkanal(0),
												 m_bLog(0),
												 m_proidlg(0)
{
	m_pPlot = new Plot(this);
	connect(m_pPlot->GetRoiPicker(), SIGNAL(RoiHasChanged()),
			this, SLOT(RedrawRoi()));

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
TmpImage* CascadeWidget::GetTmpImg() { return m_pTmpImg; }
PadImage* CascadeWidget::GetPad() { return m_pPad; }
Data2D& CascadeWidget::GetData2d() { return m_data2d; }
Plot* CascadeWidget::GetPlot() { return m_pPlot; }

void CascadeWidget::Unload()
{
	if(m_pPad) { delete m_pPad; m_pPad=NULL; }
	if(m_pTof) { delete m_pTof; m_pTof=NULL; }
	if(m_pTmpImg) { delete m_pTmpImg; m_pTmpImg=NULL; }

	m_data2d.clearData();
	ClearRoiVector();
}

void* CascadeWidget::NewPad()
{
	if(!IsPadLoaded() || IsTofLoaded() || m_bForceReinit)
	{
		Unload();
		m_pPad = new PadImage();

		m_data2d.SetImage((BasicImage**)&m_pPad);
		m_data2d.SetLog10(m_bLog);

		m_pPlot->SetData(&m_data2d, false);
		//m_pPlot->InitPlot();
		m_pPlot->ChangeRange_xy();
		m_bForceReinit=false;
	}
	// ansonsten einfach bestehendes PAD-Objekt recyclen

	return m_pPad->GetRawData();
}

void* CascadeWidget::NewTof(int iCompression)
{
	bool bCorrectCompression = 1;
	if(IsTofLoaded())
		bCorrectCompression = (m_pTof->GetCompressionMethod() == iCompression);

	if(IsPadLoaded()||!IsTofLoaded() || m_bForceReinit || !bCorrectCompression)
	{
		Unload();

		m_pTof = new TofImage(0,iCompression);
		m_pTmpImg = new TmpImage();

		m_data2d.SetImage((BasicImage**)&m_pTmpImg);
		m_data2d.SetLog10(m_bLog);

		m_pPlot->SetData(&m_data2d, false);
		//m_pPlot->InitPlot();
		m_pPlot->ChangeRange_xy();
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
		if(GlobalConfig::GuessConfigFromSize(0,int(lSize)/4, false))
		{
			ForceReinit();
			NewPad();
			iRet = m_pPad->LoadFile(pcFile);
		}
	}
	if(iRet) UpdateGraph();
	return iRet;
}

bool CascadeWidget::LoadTofFile(const char* pcFile)
{
	NewTof(TOF_COMPRESSION_NONE);
	int iRet = m_pTof->LoadFile(pcFile);

	if(iRet == LOAD_SIZE_MISMATCH)
	{
		long lSize = GetFileSize(pcFile);
		if(GlobalConfig::GuessConfigFromSize(
					m_pTof->GetCompressionMethod()==TOF_COMPRESSION_PSEUDO,
					int(lSize)/4, true))
		{
			ForceReinit();
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
		if(GlobalConfig::GuessConfigFromSize(0,uiLen/4, false))
		{
			ForceReinit();
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
		if(GlobalConfig::GuessConfigFromSize(
				m_pTof->GetCompressionMethod()==TOF_COMPRESSION_PSEUDO,
				uiLen/4, true))
		{
			ForceReinit();
			NewTof();
			iRet = m_pTof->LoadMem((unsigned int*)pcMem, uiLen/4);
		}
	}

	if(iRet) viewOverview();
	return iRet;
}

bool CascadeWidget::IsTofLoaded() const
{
	return bool(m_pTof) && bool(m_pTmpImg);
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
				m_pPlot->axisWidget(QwtPlot::yRight)->setTitle(
									m_bLog?"Counts 10^":"Counts");
				break;

			case MODE_PHASES:
			case MODE_PHASESUMS:
				m_pPlot->axisWidget(QwtPlot::yRight)->setTitle(
									m_bLog?"Phase [DEG] 10^":"Phase [DEG]");
				break;

			case MODE_CONTRASTS:
			case MODE_CONTRASTSUMS:
				m_pPlot->axisWidget(QwtPlot::yRight)->setTitle(
									m_bLog?"Contrast 10^":"Contrast");
				break;
		}
	}
	else/* if(m_pPad)*/
	{
		m_pPlot->axisWidget(QwtPlot::yRight)->setTitle(
									m_bLog?"Counts 10^":"Counts");
	}
}

void CascadeWidget::UpdateGraph()
{
	if(IsPadLoaded())
	{
		//m_pPad->UpdateRange();
		m_data2d.SetImage((BasicImage**)&m_pPad);
	}
	else if(IsTofLoaded())
	{
		if(m_iMode==MODE_SLIDES)
		{
			m_pTof->GetROI(0,m_pTof->GetTofConfig().GetImageWidth()-1, 0,
							 m_pTof->GetTofConfig().GetImageHeight()-1,
							 m_iFolie,m_iZeitkanal, m_pTmpImg);
		}
		else if(m_iMode==MODE_PHASES)
		{
			m_pTof->GetPhaseGraph(m_iFolie, m_pTmpImg);
		}
		else if(m_iMode==MODE_CONTRASTS)
		{
			m_pTof->GetContrastGraph(m_iFolie, m_pTmpImg);
		}

		m_pTmpImg->UpdateRange();
		m_data2d.SetImage((BasicImage**)&m_pTmpImg);
	}

	if(IsPadLoaded() || IsTofLoaded())
	{
		m_pPlot->SetData(&m_data2d);	// !!
		m_pPlot->replot();
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
	m_data2d.SetLog10(bLog10);
	m_pPlot->ChangeRange();
	//m_pPlot->ChangeLog(bLog10);
	UpdateGraph();
}

void CascadeWidget::UpdateRange()
{
	if(IsTofLoaded())
		GetTmpImg()->UpdateRange();
	else if(IsPadLoaded())
		GetPad()->UpdateRange();
}

void CascadeWidget::viewOverview()
{
	if(!IsTofLoaded()) return;
	SetMode(MODE_SUMS);

	GetTof()->GetOverview(m_pTmpImg);
	m_data2d.SetImage((BasicImage**)&m_pTmpImg);

	m_data2d.SetPhaseData(false);
	GetPlot()->SetColorMap(false);

	UpdateGraph();
}

void CascadeWidget::viewSlides()
{
	if(!IsTofLoaded()) return;
	SetMode(MODE_SLIDES);

	m_data2d.SetPhaseData(false);
	GetPlot()->SetColorMap(false);

	UpdateGraph();
}

void CascadeWidget::viewPhases()
{
	if(!IsTofLoaded()) return;
	SetMode(MODE_PHASES);

	m_data2d.SetPhaseData(true);
	GetPlot()->SetColorMap(true);

	UpdateGraph();
}

void CascadeWidget::viewContrasts()
{
	if(!IsTofLoaded()) return;
	SetMode(MODE_CONTRASTS);

	m_data2d.SetPhaseData(false);
	GetPlot()->SetColorMap(false);

	UpdateGraph();
}

void CascadeWidget::viewFoilSums(const bool* pbKanaele)
{
	SetMode(MODE_SUMS);
	GetTof()->AddFoils(pbKanaele, m_pTmpImg);
	m_data2d.SetImage((BasicImage**)&m_pTmpImg);

	UpdateRange();
	UpdateGraph();
}

void CascadeWidget::viewPhaseSums(const bool* pbFolien)
{
	SetMode(MODE_PHASESUMS);
	GetTof()->AddPhases(pbFolien, m_pTmpImg);
	m_data2d.SetImage((BasicImage**)&m_pTmpImg);

	UpdateRange();
	UpdateGraph();
}

void CascadeWidget::viewContrastSums(const bool* pbFolien)
{
	SetMode(MODE_CONTRASTSUMS);
	GetTof()->AddContrasts(pbFolien, m_pTmpImg);
	m_data2d.SetImage((BasicImage**)&m_pTmpImg);

	UpdateRange();
	UpdateGraph();
}

void CascadeWidget::showCalibrationDlg(int iNumBins)
{
	if(!IsTofLoaded())
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Widget: No TOF loaded.\n";

		return;
	}
	Bins bins(iNumBins, 0., 360.);

	QwtDoubleRect rect = GetPlot()->GetZoomer()->zoomRect();
	int iROIx1 = rect.left(),
	iROIx2 = rect.right(),
	iROIy1 = rect.top(),
	iROIy2 = rect.bottom();

	TmpImage* ptmpimg = new TmpImage[m_pTof->GetTofConfig().GetFoilCount()];
	for(int iFolie=0; iFolie<m_pTof->GetTofConfig().GetFoilCount(); ++iFolie)
		GetTof()->GetPhaseGraph(iFolie, ptmpimg+iFolie, /*iROIx1, iROIx2,
														iROIy1, iROIy2,*/ true);

	int iW = iROIx2-iROIx1; if(iW<0) iW=-iW;
	int iH = iROIy2-iROIy1; if(iH<0) iH=-iH;

	for(int iFolie=0; iFolie<m_pTof->GetTofConfig().GetFoilCount(); ++iFolie)
		for(int iY=0; iY<iH; ++iY)
			for(int iX=0; iX<iW; ++iX)
			{
				double dVal = ptmpimg[iFolie].GetData(iX,iY);
				if(dVal==0.) continue;
				bins.Inc(dVal);
			}
	delete[] ptmpimg;

	CalibrationDlg CalDlg(this, bins);
	CalDlg.exec();
}

void CascadeWidget::showGraphDlg()
{
	if(!IsTofLoaded())
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Widget: No TOF loaded.\n";

		return;
	}

	/*QwtDoubleRect rect = GetPlot()->GetZoomer()->zoomRect();
	int iROIx1 = rect.left(),
	iROIx2 = rect.right(),
	iROIy1 = rect.top(),
	iROIy2 = rect.bottom();*/

	GraphDlg graphdlg(this, GetTof(), m_iFolie);
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
	if(!IsTofLoaded())
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Widget: No TOF loaded.\n";

		return;
	}

	static SumDlg *pSummenDlgSlides = NULL;
	static SumDlgNoChannels *pSummenDlgPhases = NULL;
	static SumDlgNoChannels *pSummenDlgContrasts = NULL;

	switch(GetMode())
	{
		case MODE_SLIDES:
		case MODE_SUMS:
			if(!pSummenDlgSlides)
			{
				pSummenDlgSlides = new SumDlg(this);
				connect(pSummenDlgSlides, SIGNAL(SumSignal(const bool *, int)),
						this, SLOT(SumDlgSlot(const bool *, int)));
			}

			pSummenDlgSlides->SetMode(GetMode());
			pSummenDlgSlides->show();
			pSummenDlgSlides->raise();
			pSummenDlgSlides->activateWindow();
			break;

		case MODE_PHASES:
		case MODE_PHASESUMS:
			if(!pSummenDlgPhases)
			{
				pSummenDlgPhases = new SumDlgNoChannels(this);
				connect(pSummenDlgPhases, SIGNAL(SumSignal(const bool *, int)),
						this, SLOT(SumDlgSlot(const bool *, int)));
			}

			pSummenDlgPhases->SetMode(GetMode());
			pSummenDlgPhases->show();
			pSummenDlgPhases->raise();
			pSummenDlgPhases->activateWindow();
			break;

		case MODE_CONTRASTS:
		case MODE_CONTRASTSUMS:
			if(!pSummenDlgContrasts)
			{
				pSummenDlgContrasts = new SumDlgNoChannels(this);
				connect(pSummenDlgContrasts, SIGNAL(SumSignal(const bool *, int)),
						this, SLOT(SumDlgSlot(const bool *, int)));
			}

			pSummenDlgContrasts->SetMode(GetMode());
			pSummenDlgContrasts->show();
			pSummenDlgContrasts->raise();
			pSummenDlgContrasts->activateWindow();
			break;
	}
}

void CascadeWidget::showRoiDlg()
{
	if(!IsTofLoaded() && !IsPadLoaded())
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Widget: Neither TOF nor PAD loaded.\n";

		return;
	}

	Roi *pRoi = 0;
	bool bUseRoi = false;

	if(IsTofLoaded())
	{
		pRoi = &GetTof()->GetRoi();
		bUseRoi = GetTof()->GetUseRoi();

	}
	else if(IsPadLoaded())
	{
		pRoi = &GetPad()->GetRoi();
		bUseRoi = GetPad()->GetUseRoi();
	}


	if(!m_proidlg)
	{
		m_proidlg = new RoiDlg(this);
		connect(m_proidlg->buttonBox, SIGNAL(clicked(QAbstractButton*)),
				this, SLOT(RoiDlgAccepted(QAbstractButton*)));
	}

	m_proidlg->SetRoi(pRoi);

	m_proidlg->checkBoxUseRoi->setCheckState(bUseRoi ? Qt::Checked
													 : Qt::Unchecked);

	m_proidlg->show();
	m_proidlg->raise();
	m_proidlg->activateWindow();
}

void CascadeWidget::RoiDlgAccepted(QAbstractButton* pBtn)
{
	Roi *pRoi = 0;

	if(IsTofLoaded())
		pRoi = &GetTof()->GetRoi();
	else if(IsPadLoaded())
		pRoi = &GetPad()->GetRoi();


	// "OK" or "Apply" clicked?
	if(m_proidlg->buttonBox->standardButton(pBtn) == QDialogButtonBox::Apply ||
	   m_proidlg->buttonBox->standardButton(pBtn) == QDialogButtonBox::Ok)
	{
		(*pRoi) = (*m_proidlg->GetRoi());

		bool bCk = (m_proidlg->checkBoxUseRoi->checkState() == Qt::Checked);

		if(IsTofLoaded())
			GetTof()->UseRoi(bCk);
		else if(IsPadLoaded())
			GetPad()->UseRoi(bCk);

		RedrawRoi();
	}
}

bool CascadeWidget::LoadRoi(const char* pcFile)
{
	if(!IsTofLoaded() && !IsPadLoaded())
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Widget: Neither TOF nor PAD loaded.\n";

		return false;
	}

	Roi *pRoi = 0;

	if(IsTofLoaded())
		pRoi = &GetTof()->GetRoi();
	else if(IsPadLoaded())
		pRoi = &GetPad()->GetRoi();

	int iRet = pRoi->Load(pcFile);

	if(IsTofLoaded())
		GetTof()->UseRoi(true);
	else if(IsPadLoaded())
		GetPad()->UseRoi(true);

	RedrawRoi();
	return iRet;
}

bool CascadeWidget::SaveRoi(const char* pcFile)
{
	if(!IsTofLoaded() && !IsPadLoaded())
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Widget: Neither TOF nor PAD loaded.\n";

		return false;
	}

	Roi *pRoi = 0;

	if(IsTofLoaded())
		pRoi = &GetTof()->GetRoi();
	else if(IsPadLoaded())
		pRoi = &GetPad()->GetRoi();

	return pRoi->Save(pcFile);
}

void CascadeWidget::ForceReinit() { m_bForceReinit = true; }


//----------------------------------------------------------------------
// ROI curves

Roi* CascadeWidget::GetCurRoi()
{
	Roi *pRoi = 0;

	if(IsTofLoaded())
		pRoi = &GetTof()->GetRoi();
	else if(IsPadLoaded())
		pRoi = &GetPad()->GetRoi();

	return pRoi;
}

void CascadeWidget::UpdateRoiVector()
{
	if(!IsTofLoaded() && !IsPadLoaded())
		return;

	Roi *pRoi = GetCurRoi();
	ClearRoiVector();

	for(int i=0; i<pRoi->GetNumElements(); ++i)
	{
		RoiElement& elem = pRoi->GetElement(i);

		QwtPlotCurve* pcurve = new QwtPlotCurve;
		m_vecRoiCurves.push_back(pcurve);

		pcurve->setRenderHint(QwtPlotItem::RenderAntialiased);
		QPen pen = QPen(Qt::white);
		pen.setWidthF(1.5);
		pcurve->setPen(pen);

		const int iVertexCount = elem.GetVertexCount();

		double *pdx = new double[iVertexCount+1];
		double *pdy = new double[iVertexCount+1];

		for(int iVertex=0; iVertex<iVertexCount; ++iVertex)
		{
			Vec2d<double> vec = elem.GetVertex(iVertex);
			pdx[iVertex] = vec[0];
			pdy[iVertex] = vec[1];
			//std::cout << vec << std::endl;

			if(iVertex==0)
			{
				pdx[iVertexCount] = vec[0];
				pdy[iVertexCount] = vec[1];
			}
		}

		pcurve->setData(pdx, pdy, iVertexCount+1);

		delete[] pdx;
		delete[] pdy;

		pcurve->attach(m_pPlot);
	}
}

void CascadeWidget::ClearRoiVector()
{
	for(unsigned int i=0; i<m_vecRoiCurves.size(); ++i)
	{
		if(m_vecRoiCurves[i])
		{
			m_vecRoiCurves[i]->detach();
			delete m_vecRoiCurves[i];
		}
	}
	m_vecRoiCurves.clear();
}

void CascadeWidget::RedrawRoi()
{
	bool bUseRoi = false;

	if(IsTofLoaded())
		bUseRoi = GetTof()->GetUseRoi();
	else if(IsPadLoaded())
		bUseRoi = GetPad()->GetUseRoi();

	if(bUseRoi)
	{
		UpdateRoiVector();
		m_pPlot->replot();
	}
	else
	{
		ClearRoiVector();
		m_pPlot->replot();
	}
}

void CascadeWidget::ClearRoi()
{
	Roi* pRoi = GetCurRoi();
	if(!pRoi) return;

	pRoi->clear();
	ClearRoiVector();
	RedrawRoi();
}

void CascadeWidget::SetRoiDrawMode(int iMode)
{
	MainPicker* pPicker = (MainPicker*)GetPlot()->GetRoiPicker();

	if(iMode == ROI_DRAW_NONE)
	{
		pPicker->setEnabled(false);
		GetPlot()->GetZoomer()->setEnabled(true);

		pPicker->SetCurRoi(0);
	}
	else
	{
		if(IsTofLoaded())
			GetTof()->UseRoi(true);
		else if(IsPadLoaded())
			GetPad()->UseRoi(true);

		Roi *pRoi = GetCurRoi();
		pPicker->SetCurRoi(pRoi);
		pPicker->SetRoiDrawMode(iMode);

		GetPlot()->GetZoomer()->setEnabled(false);
		pPicker->setEnabled(true);
	}
}

//----------------------------------------------------------------------
