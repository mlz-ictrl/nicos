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

#include "../main/cascadewidget.h"
#include "../loader/tofloader.h"
#include "../plot/tofdata.h"
#include "../plot/bins.h"
#include "../dialogs/cascadedialogs.h"
#include "../auxiliary/helper.h"
#include "../auxiliary/logger.h"

#include <QPrinter>
#include <iostream>


CascadeWidget::CascadeWidget(QWidget *pParent) : QWidget(pParent),
												 m_bForceReinit(0),
												 m_pPad(0),
												 m_pTof(0),
												 m_pTmpImg(0),
												 m_iMode(MODE_OVERVIEW),
												 m_iFolie(0),
												 m_iZeitkanal(0),
												 m_bLog(0),
												 m_proidlg(0),
												 m_pbrowsedlg(0),
												 m_pintdlg(0),
												 m_pRangeDlg(0),
												 m_pCountsVsImagesDlg(0),
												 m_pContrastsVsImagesDlg(0),
												 m_pparamdlg(0)
{
	m_pPlot = new Plot(this);

	connect(m_pPlot->GetRoiPicker(), SIGNAL(RoiHasChanged()),
			this, SLOT(RoiHasChanged()));
	connect(this, SIGNAL(FileHasChanged(const char*)),
			this, SLOT(_FileHasChanged(const char*)));

	QGridLayout *gridLayout = new QGridLayout(this);
	gridLayout->addWidget(m_pPlot,0,0,1,1);
	this->setLayout(gridLayout);

	UpdateLabels();
}

CascadeWidget::~CascadeWidget()
{
	Unload();
	//if(m_pPlot) delete m_pPlot;
}

TofImage* CascadeWidget::GetTof() { return m_pTof; }
TmpImage* CascadeWidget::GetTmpImg() { return m_pTmpImg; }
PadImage* CascadeWidget::GetPad() { return m_pPad; }
MainRasterData& CascadeWidget::GetData2d() { return m_data2d; }
Plot* CascadeWidget::GetPlot() { return m_pPlot; }

void CascadeWidget::Unload()
{
	MainPicker* pPicker = (MainPicker*)GetPlot()->GetRoiPicker();
	pPicker->SetCurRoi(0);
	ClearRoiVector();

	if(m_pPad) { delete m_pPad; m_pPad=NULL; }
	if(m_pTof) { delete m_pTof; m_pTof=NULL; }
	if(m_pTmpImg) { delete m_pTmpImg; m_pTmpImg=NULL; }

	m_data2d.clearData();
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

void* CascadeWidget::NewTof()
{
	if(IsPadLoaded()||!IsTofLoaded() || m_bForceReinit)
	{
		Unload();

		m_pTof = new TofImage(0);
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

bool CascadeWidget::LoadFile(const char* pcFile)
{
	std::string strFileType = GetFileEnding(pcFile);

	if(strFileType=="pad" || strFileType=="PAD" || strFileType=="pad.gz" || strFileType=="PAD.GZ")
		return LoadPadFile(pcFile);
	else if(strFileType=="tof" || strFileType=="TOF" || strFileType=="tof.gz" || strFileType=="TOF.GZ")
		return LoadTofFile(pcFile);
	else // guessing file type
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "Widget: Unknown file extension \"" << strFileType
			   << "\", guessing type.\n";

		// try to load as PAD file
		if(LoadPadFile(pcFile))
			return true;

		// if this didn't work, try to load as TOF file
		if(LoadTofFile(pcFile))
			return true;
	}

	return false;
}

bool CascadeWidget::LoadPadFile(const char* pcFile, bool bBinary)
{
	NewPad();

	int iRet;
	if(bBinary)
		iRet= m_pPad->LoadFile(pcFile);
	else
		iRet= m_pPad->LoadTextFile(pcFile);

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
	if(iRet)
	{
		UpdateGraph();
		emit FileHasChanged(pcFile);
	}
	updateFileParams();

	return iRet;
}

bool CascadeWidget::LoadPadFile(const char* pcFile)
{ return LoadPadFile(pcFile, 1); }

bool CascadeWidget::LoadPadFileTxt(const char* pcFile)
{ return LoadPadFile(pcFile, 0); }

bool CascadeWidget::LoadTofFile(const char* pcFile)
{
	NewTof();
	int iRet = m_pTof->LoadFile(pcFile);

	if(iRet == LOAD_SIZE_MISMATCH)
	{
		long lSize = GetFileSize(pcFile);
		if(GlobalConfig::GuessConfigFromSize(
					m_pTof->GetTofConfig().GetPseudoCompression(),
					int(lSize)/4, true))
		{
			ForceReinit();
			NewTof();
			iRet = m_pTof->LoadFile(pcFile);
		}
	}

	if(iRet)
	{
		//viewOverview();
		UpdateGraph();
		emit FileHasChanged(pcFile);
	}

	updateFileParams();
	return iRet;
}

bool CascadeWidget::LoadPadMem(const char* pcMem, unsigned int uiLen)
{
	NewPad();
	int iRet = m_pPad->LoadMem(pcMem, uiLen);

	if(iRet == LOAD_SIZE_MISMATCH)
	{
		if(GlobalConfig::GuessConfigFromSize(0,uiLen/4, false))
		{
			ForceReinit();
			NewPad();
			iRet = m_pPad->LoadMem(pcMem, uiLen);
		}
	}

	if(iRet)
	{
		UpdateGraph();
		emit FileHasChanged("<memfile>");
	}

	updateFileParams();
	return iRet;
}

bool CascadeWidget::LoadTofMem(const char* pcMem, unsigned int uiLen)
{
	NewTof();
	int iRet = m_pTof->LoadMem(pcMem, uiLen);

	if(iRet == LOAD_SIZE_MISMATCH)
	{
		if(GlobalConfig::GuessConfigFromSize(
				m_pTof->GetTofConfig().GetPseudoCompression(),
				uiLen/4, true))
		{
			ForceReinit();
			NewTof();
			iRet = m_pTof->LoadMem(pcMem, uiLen);
		}
	}

	if(iRet)
	{
		//viewOverview();
		UpdateGraph();
		emit FileHasChanged("<memfile>");
	}

	updateFileParams();
	return iRet;
}

void CascadeWidget::_FileHasChanged(const char* pcFile)
{
	if(m_pRangeDlg)
		m_pRangeDlg->Update();
}

bool CascadeWidget::IsTofLoaded() const
{
	return bool(m_pTof) && bool(m_pTmpImg);
}

bool CascadeWidget::IsPadLoaded() const
{
	return bool(m_pPad);
}

unsigned int CascadeWidget::GetCounts() const
{
	if(IsTofLoaded())
		return m_pTof->GetCounts();
	else if(IsPadLoaded())
		return m_pPad->GetCounts();

	return 0;
}

void CascadeWidget::UpdateLabels()
{
	if(m_pTof)
	{
		switch(m_iMode)
		{
			case MODE_SLIDES:
			case MODE_SUMS:
			case MODE_OVERVIEW:
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
			m_pTmpImg->Clear();
			*m_pTmpImg = m_pTof->GetROI(0,
							 m_pTof->GetTofConfig().GetImageWidth(), 0,
							 m_pTof->GetTofConfig().GetImageHeight(),
							 m_iFolie,m_iZeitkanal);
		}
		else if(m_iMode==MODE_PHASES)
		{
			m_pTmpImg->Clear();
			*m_pTmpImg = m_pTof->GetPhaseGraph(m_iFolie);
		}
		else if(m_iMode==MODE_CONTRASTS)
		{
			m_pTmpImg->Clear();
			*m_pTmpImg = m_pTof->GetContrastGraph(m_iFolie);
		}
		else if(m_iMode==MODE_OVERVIEW)
		{
			m_pTmpImg->Clear();
			*m_pTmpImg = GetTof()->GetOverview();
		}

		m_pTmpImg->UpdateRange();
		m_data2d.SetImage((BasicImage**)&m_pTmpImg);
	}

	if(IsPadLoaded() || IsTofLoaded())
	{
		m_pPlot->SetData(&m_data2d);	// !!

		RedrawRoi();
		//m_pPlot->replot();
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
	if(m_bLog == bLog10)
		return;

	m_bLog = bLog10;

	// update range dialog
	if(m_pRangeDlg)
	{
		QwtDoubleInterval range = m_data2d.range();

		double dMin = range.minValue();
		double dMax = range.maxValue();

		if(bLog10)
		{
			dMin = safe_log10_lowerrange(dMin);
			dMax = safe_log10_lowerrange(dMax);
		}
		else
		{
			dMin = pow(10.,dMin);
			dMax = pow(10.,dMax);
		}

		m_pRangeDlg->SetReadOnly(true);
		m_pRangeDlg->spinBoxMin->setValue(dMin);
		m_pRangeDlg->spinBoxMax->setValue(dMax);
		m_pRangeDlg->SetReadOnly(false);

		// if manual range is set -> update plot with converted range
		if(!m_data2d.GetAutoCountRange())
			SetCountRange(dMin, dMax);
	}

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
	SetMode(MODE_OVERVIEW);

	m_pTmpImg->Clear();
	*m_pTmpImg = GetTof()->GetOverview();
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
	m_pTmpImg->Clear();
	*m_pTmpImg = GetTof()->AddFoils(pbKanaele);
	m_data2d.SetImage((BasicImage**)&m_pTmpImg);

	UpdateRange();
	UpdateGraph();
}

void CascadeWidget::viewPhaseSums(const bool* pbFolien)
{
	SetMode(MODE_PHASESUMS);
	m_pTmpImg->Clear();
	*m_pTmpImg = GetTof()->AddPhases(pbFolien);
	m_data2d.SetImage((BasicImage**)&m_pTmpImg);

	UpdateRange();
	UpdateGraph();
}

void CascadeWidget::viewContrastSums(const bool* pbFolien)
{
	SetMode(MODE_CONTRASTSUMS);
	m_pTmpImg->Clear();
	*m_pTmpImg = GetTof()->AddContrasts(pbFolien);
	m_data2d.SetImage((BasicImage**)&m_pTmpImg);

	UpdateRange();
	UpdateGraph();
}



//------------------------------------------------------------------------------
// dialogs

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
		*(ptmpimg+iFolie) = GetTof()->GetPhaseGraph(iFolie, true);

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
		case MODE_OVERVIEW:
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
		case MODE_OVERVIEW:
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

void CascadeWidget::showBrowseDlg(const char* pcDir)
{
	if(pcDir)
		GlobalConfig::SetCurDir(pcDir);

	if(!m_pbrowsedlg)
		m_pbrowsedlg = new BrowseDlg(this);
	else
		m_pbrowsedlg->SetDir();

	QPoint pt = mapToGlobal(pos());
	m_pbrowsedlg->move(pt.x()+width(),pt.y());
	m_pbrowsedlg->show();
	m_pbrowsedlg->raise();
	m_pbrowsedlg->activateWindow();
}

void CascadeWidget::showIntegrationDlg()
{
	if(!m_pintdlg)
		m_pintdlg = new IntegrationDlg(this);

	m_pintdlg->show();
	m_pintdlg->raise();
	m_pintdlg->activateWindow();

	m_pintdlg->UseBeamCenter();
}

void CascadeWidget::showRangeDlg()
{
	if(!m_pRangeDlg)
		m_pRangeDlg = new RangeDlg(this);

	m_pRangeDlg->Update();

	m_pRangeDlg->show();
	m_pRangeDlg->raise();
	m_pRangeDlg->activateWindow();
}

void CascadeWidget::showRoiDlg()
{
	if(!IsTofLoaded() && !IsPadLoaded())
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Widget: Neither TOF nor PAD loaded.\n";

		return;
	}

	Roi *pRoi = GetCurRoi();
	if(!pRoi) return;

	bool bUseRoi = IsRoiInUse();

	if(!m_proidlg)
		m_proidlg = new RoiDlg(this);

	m_proidlg->SetRoi(pRoi);

	m_proidlg->checkBoxUseRoi->setCheckState(bUseRoi ? Qt::Checked
													 : Qt::Unchecked);

	m_proidlg->show();
	m_proidlg->raise();
	m_proidlg->activateWindow();
}

void CascadeWidget::RoiDlgAccepted(QAbstractButton* pBtn)
{
	Roi *pRoi = GetCurRoi();
	if(!pRoi) return;

	// "OK" or "Apply" clicked?
	if(m_proidlg->buttonBox->standardButton(pBtn) == QDialogButtonBox::Apply ||
	   m_proidlg->buttonBox->standardButton(pBtn) == QDialogButtonBox::Ok)
	{
		(*pRoi) = (*m_proidlg->GetRoi());

		bool bCk = (m_proidlg->checkBoxUseRoi->checkState() == Qt::Checked);

		UseRoi(bCk);
		RedrawRoi();
	}
}

void CascadeWidget::showCountsVsImagesDlg()
{
	if(!m_pCountsVsImagesDlg)
		m_pCountsVsImagesDlg = new CountsVsImagesDlg(this);

	m_pCountsVsImagesDlg->show();
	m_pCountsVsImagesDlg->raise();
	m_pCountsVsImagesDlg->activateWindow();
}

void CascadeWidget::showContrastsVsImagesDlg()
{
	if(!m_pContrastsVsImagesDlg)
		m_pContrastsVsImagesDlg = new ContrastsVsImagesDlg(this);

	m_pContrastsVsImagesDlg->show();
	m_pContrastsVsImagesDlg->raise();
	m_pContrastsVsImagesDlg->activateWindow();
}
//------------------------------------------------------------------------------



bool CascadeWidget::LoadRoi(const char* pcFile)
{
	if(!IsTofLoaded() && !IsPadLoaded())
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Widget: Neither TOF nor PAD loaded.\n";

		return false;
	}

	Roi *pRoi = GetCurRoi();
	if(!pRoi) return false;

	int iRet = pRoi->Load(pcFile);

	UseRoi(true);

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

	Roi *pRoi = GetCurRoi();
	if(!pRoi) return false;

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

bool CascadeWidget::IsRoiInUse()
{
	if(IsTofLoaded())
		return GetTof()->GetUseRoi();
	else if(IsPadLoaded())
		return GetPad()->GetUseRoi();

	return false;
}

void CascadeWidget::UseRoi(bool bUse)
{
	if(IsTofLoaded())
		GetTof()->UseRoi(bUse);
	else if(IsPadLoaded())
		GetPad()->UseRoi(bUse);
}

void CascadeWidget::UpdateRoiVector()
{
	if(!IsTofLoaded() && !IsPadLoaded())
		return;

	Roi *pRoi = GetCurRoi();
	if(!pRoi) return;

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

void CascadeWidget::RoiHasChanged()
{
	UseRoi(true);
	RedrawRoi();

	emit FileHasChanged();
}

void CascadeWidget::RedrawRoi()
{
	bool bUseRoi = IsRoiInUse();
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

	UseRoi(false);

	pRoi->clear();
	ClearRoiVector();
	RedrawRoi();

	emit FileHasChanged();
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
		UseRoi(true);

		Roi *pRoi = GetCurRoi();
		if(!pRoi) return;

		pPicker->SetCurRoi(pRoi);
		pPicker->SetRoiDrawMode(iMode);

		GetPlot()->GetZoomer()->setEnabled(false);
		pPicker->setEnabled(true);
	}
}
//------------------------------------------------------------------------------



void CascadeWidget::SetAutoCountRange(bool bAuto)
{
	if(!GetPlot()) return;

	GetData2d().SetAutoCountRange(bAuto);
	GetPlot()->ChangeRange();
	UpdateGraph();
}

void CascadeWidget::SetCountRange(double dMin, double dMax)
{
	if(!GetPlot()) return;

	GetData2d().SetCountRange(dMin, dMax);
	GetPlot()->ChangeRange();
	UpdateGraph();
}



//------------------------------------------------------------------------------

bool CascadeWidget::ToPDF(const char* pcDst) const
{
	QPrinter printer;
	printer.setColorMode(QPrinter::Color);
	printer.setOrientation(QPrinter::Landscape);
	printer.setOutputFileName(QString(pcDst));
	printer.setOutputFormat(QPrinter::PdfFormat);

	m_pPlot->print(printer);
	return true;
}

bool CascadeWidget::updateFileParams()
{
	if(!m_pparamdlg)
		return false;

	const CascConf* pConf = 0;

	if(IsTofLoaded())
		pConf = &this->m_pTof->GetLocalConfig();
	else if(IsPadLoaded())
		pConf = &this->m_pPad->GetLocalConfig();
	else
		return false;

	m_pparamdlg->updateParams(pConf);

	return true;
}

void CascadeWidget::showFileParams()
{
	if(!m_pparamdlg)
		m_pparamdlg = new FileParamDlg(this);

	if(!updateFileParams())
		return;

	m_pparamdlg->show();
	m_pparamdlg->activateWindow();
}

/*
#ifdef __MOC_EXTERN_BUILD__
//	// Qt-Metaobjekte
	#include "cascadewidget.moc"
#endif
*/
