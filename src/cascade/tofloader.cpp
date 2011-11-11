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
// Klassen zum Laden und Verarbeiten von Tof- & Pad-Dateien

#include "tofloader.h"

#include <fstream>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <vector>
#include <string.h>
#include <limits>
#include "logger.h"
#include "helper.h"

#ifdef USE_MINUIT
	#include <Minuit2/FCNBase.h>
	#include <Minuit2/FunctionMinimum.h>
	#include <Minuit2/MnMigrad.h>
	#include <Minuit2/MnSimplex.h>
	#include <Minuit2/MnMinimize.h>
	#include <Minuit2/MnFumiliMinimize.h>
	#include <Minuit2/MnUserParameters.h>
	#include <Minuit2/MnPrint.h>
#endif


// *************** TOF *********************************************************
TofImage::TofImage(const char *pcFileName, int iCompressed, bool bExternalMem,
				   const TofConfig* conf)
		: m_bExternalMem(bExternalMem)
{
	SetCompressionMethod(iCompressed);
	m_puiDaten = 0;
	m_bUseRoi = false;

	if(conf)	// use given config
		m_config = *conf;
	else 		// if no config is given, copy global one
		m_config = GlobalConfig::GetTofConfig();

	logger.SetCurLogLevel(LOGLEVEL_INFO);
	logger << "Loader: New TOF image: " << "external mem=" << m_bExternalMem
			  << ", width=" << GetTofConfig().GetImageWidth()
			  << ", height=" << GetTofConfig().GetImageHeight()
			  << ", images=" << GetTofConfig().GetImageCount()
			  << ", comp=" << GetCompressionMethod()
			  << ".\n";

	// should TofImage manage its own memory?
	if(!m_bExternalMem)
	{
		int iSize = GetTofSize();
		m_puiDaten = new unsigned int[iSize];
		if(m_puiDaten==NULL)
		{
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "Loader: Could not allocate memory (line "
				   << __LINE__ << ")!\n";
			return;
		}

		if(pcFileName)
			LoadFile(pcFileName);
		else
			memset(m_puiDaten,0,iSize*sizeof(int));
	}
}

TofImage::~TofImage()
{
	Clear();
}

void TofImage::UseRoi(bool bUseRoi) { m_bUseRoi = bUseRoi; }
Roi& TofImage::GetRoi() { return m_roi; }
bool TofImage::GetUseRoi() const { return m_bUseRoi; };

const TofConfig& TofImage::GetTofConfig() const
{
	return m_config;
}

void TofImage::SetExternalMem(void* pvDaten)
{
	if(!m_bExternalMem)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: This TOF does not use external memory"
				  " (line " << __LINE__ << ")!\n";
		return;
	}

	m_puiDaten = (unsigned int*)pvDaten;
	//UpdateRange();
}

int TofImage::GetTofSize() const
{
	int iSize = m_bPseudoCompressed
			? GetTofConfig().GetFoilCount()*
			  GetTofConfig().GetImagesPerFoil()*
			  GetTofConfig().GetImageHeight()*
			  GetTofConfig().GetImageWidth()
			: GetTofConfig().GetImageCount()*
			  GetTofConfig().GetImageHeight()*
			  GetTofConfig().GetImageWidth();
	return iSize;
}

void TofImage::Clear(void)
{
	if(m_puiDaten && !m_bExternalMem)
	{
		delete[] m_puiDaten;
		m_puiDaten=NULL;
	}
}

int TofImage::GetCompressionMethod() const
{
	if(m_bPseudoCompressed)
		return TOF_COMPRESSION_PSEUDO;
	return TOF_COMPRESSION_NONE;
}

void TofImage::SetCompressionMethod(int iComp)
{
	switch(iComp)
	{
		case TOF_COMPRESSION_NONE:
			m_bPseudoCompressed=0;
			break;
		case TOF_COMPRESSION_PSEUDO:
			m_bPseudoCompressed=1;
			break;
		case TOF_COMPRESSION_USEGLOBCONFIG:
			m_bPseudoCompressed=GetTofConfig().GetPseudoCompression();
			break;
		default:
			m_bPseudoCompressed=1;
			break;
	}
}

unsigned int TofImage::GetData(int iBild, int iX, int iY) const
{
	if(m_puiDaten && iBild>=0 && iBild<GetTofConfig().GetImageCount() &&
	   iX>=0 && iX<GetTofConfig().GetImageWidth() &&
	   iY>=0 && iY<GetTofConfig().GetImageHeight())
		return m_puiDaten[iBild*GetTofConfig().GetImageWidth()*
							    GetTofConfig().GetImageHeight() +
								iY*GetTofConfig().GetImageWidth() + iX];

	return 0;
}

unsigned int TofImage::GetData(int iFoil, int iTimechannel,
							   int iX, int iY) const
{
	if(!m_bPseudoCompressed)
	{
		int iZ = GetTofConfig().GetFoilBegin(iFoil) + iTimechannel;

		if(iTimechannel!=0)
			return GetData(iZ,iX,iY);
		else
			return GetData(iZ,iX,iY)+
				   GetData(iZ+GetTofConfig().GetImagesPerFoil(), iX, iY);
	}
	else
	{
		return GetData(iFoil*GetTofConfig().GetImagesPerFoil()
						+ iTimechannel, iX, iY);
	}
}

unsigned int TofImage::GetDataInsideROI(int iFoil, int iTimechannel,
										int iX, int iY) const
{
	if(m_bUseRoi)
	{
		// only continue if point is in ROI
		if(!m_roi.IsInside(iX, iY))
			return 0;
	}

	return GetData(iFoil, iTimechannel, iX, iY);
}

unsigned int TofImage::GetDataInsideROI(int iImage, int iX, int iY) const
{
	if(m_bUseRoi)
	{
		// only continue if point is in ROI
		if(!m_roi.IsInside(iX, iY))
			return 0;
	}

	return GetData(iImage, iX, iY);
}

unsigned int* TofImage::GetRawData(void) const
{
	return m_puiDaten;
}

int TofImage::LoadMem(const unsigned int *puiBuf, unsigned int uiBufLen)
{
	if(m_bExternalMem)
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "Loader: This TOF uses external memory"
				  " (line " << __LINE__ << ")!\n";
	}

	int iSize = GetTofSize();

	if(uiBufLen!=(unsigned int)iSize)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Buffer size (" << uiBufLen << " ints) != TOF size ("
			   << iSize << " ints)." << "\n";
		return LOAD_SIZE_MISMATCH;
	}

	memcpy(m_puiDaten, puiBuf, sizeof(int)*iSize);

// falls PowerPC, ints von little zu big endian konvertieren
#ifdef __BIG_ENDIAN__
	for(int i=0; i<iExpectedSize; ++i)
		m_puiDaten[i] = endian_swap(m_puiDaten[i]);
#endif
	return LOAD_SUCCESS;
}

int TofImage::LoadFile(const char *pcFileName)
{
	if(m_bExternalMem)
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "Loader: This TOF uses external memory"
				  " (line " << __LINE__ << ")!\n";
	}

	int iSize = GetTofSize();
	int iRet = LOAD_SUCCESS;

	FILE *pf = fopen(pcFileName,"rb");
	if(!pf)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not open file \"" << pcFileName << "\"."
			   << "\n";
		return LOAD_FAIL;
	}

	unsigned int uiBufLen = fread(m_puiDaten, sizeof(unsigned int), iSize, pf);
	if(!uiBufLen)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not read file \"" << pcFileName << "\"."
			   << "\n";
	}
	if(uiBufLen!=(unsigned int)iSize)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Buffer size (" << uiBufLen << " ints) != TOF size ("
			   << iSize << " ints)." << "\n";
		iRet = LOAD_SIZE_MISMATCH;
	}

	fclose(pf);

// falls PowerPC, ints von little zu big endian konvertieren
#ifdef __BIG_ENDIAN__
	for(int i=0; i<iExpectedSize; ++i)
		m_puiDaten[i] = endian_swap(m_puiDaten[i]);
#endif
	return iRet;
}

// GetROI
void TofImage::GetROI(int iStartX, int iEndX, int iStartY, int iEndY,
					  int iFolie, int iTimechannel, TmpImage *pImg) const
{
	if(!pImg) return;

	GetTofConfig().CheckTofArguments(&iStartX, &iEndX, &iStartY, &iEndY,
								  &iFolie, &iTimechannel);

	int iBildBreite = abs(iEndX-iStartX);
	int iBildHoehe = abs(iEndY-iStartY);

	unsigned int *puiWave = new unsigned int[iBildHoehe*iBildBreite];
	if(puiWave==NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line "
			   << __LINE__ << ")!\n";
		return;
	}

	pImg->Clear();
	pImg->m_iW = iBildBreite;
	pImg->m_iH = iBildHoehe;
	pImg->m_puiDaten = puiWave;

	for(int iY=iStartY; iY<iEndY; ++iY)
		for(int iX=iStartX; iX<iEndX; ++iX)
			puiWave[(iX-iStartX) + (iY-iStartY)*iBildBreite] =
											GetData(iFolie,iTimechannel,iX,iY);
}

// TOF-Graph
void TofImage::GetGraph(int iStartX, int iEndX, int iStartY, int iEndY,
						int iFolie, TmpGraph* pGraph) const
{
	if(!pGraph) return;
	GetTofConfig().CheckTofArguments(&iStartX,&iEndX,&iStartY,&iEndY,&iFolie);

	unsigned int *puiWave = new unsigned int[GetTofConfig().GetImagesPerFoil()];

	pGraph->m_iW = GetTofConfig().GetImagesPerFoil();
	pGraph->m_puiDaten = puiWave;

	for(int iZ0=0; iZ0<GetTofConfig().GetImagesPerFoil(); ++iZ0)
	{
		unsigned int uiSummedVal=0;
		for(int iY=iStartY; iY<iEndY; ++iY)
			for(int iX=iStartX; iX<iEndX; ++iX)
				uiSummedVal += GetDataInsideROI(iFolie, iZ0, iX, iY);

		puiWave[iZ0]=uiSummedVal;
	}
}

void TofImage::GetGraph(int iFoil, TmpGraph* pGraph) const
{
	int iStartX = 0,
		iStartY = 0,
		iEndX = GetTofConfig().GetImageWidth(),
		iEndY = GetTofConfig().GetImageHeight();

	GetGraph(iStartX, iEndX, iStartY, iEndY, iFoil, pGraph);
}

void TofImage::GetTotalGraph(int iStartX, int iEndX, int iStartY, int iEndY,
							 double dPhaseShift, TmpGraph* pGraph) const
{
	if(!pGraph) return;

	GetTofConfig().CheckTofArguments(&iStartX, &iEndX, &iStartY, &iEndY);
	unsigned int *puiWave = new unsigned int[GetTofConfig().GetImagesPerFoil()];

	pGraph->m_iW = GetTofConfig().GetImagesPerFoil();
	pGraph->m_puiDaten = puiWave;

	// Zeitkanäle
	for(int iZ0=0; iZ0<GetTofConfig().GetImagesPerFoil(); ++iZ0)
	{
		unsigned int uiSummedVal=0;
		for(int iY=iStartY; iY<iEndY; ++iY)
		{
			for(int iX=iStartX; iX<iEndX; ++iX)
			{
				// Folien
				for(int iFolie=0; iFolie<GetTofConfig().GetFoilCount();++iFolie)
				{
					int iShift = iZ0 + int(dPhaseShift*double(iFolie));
					if(iShift>=GetTofConfig().GetImagesPerFoil())
						iShift%=GetTofConfig().GetImagesPerFoil();

					uiSummedVal += GetDataInsideROI(iFolie, iShift, iX, iY);
				}
			}
		}
		puiWave[iZ0]=uiSummedVal;
	}
}

// Summe aller Bilder
void TofImage::GetOverview(TmpImage *pImg) const
{
	pImg->Clear();
	pImg->m_iW = GetTofConfig().GetImageWidth();
	pImg->m_iH = GetTofConfig().GetImageHeight();

	pImg->m_puiDaten = new unsigned int[GetTofConfig().GetImageWidth()*
										GetTofConfig().GetImageHeight()];
	if(pImg->m_puiDaten==NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line "
			   << __LINE__ << ")!\n";
		return;
	}
	memset(pImg->m_puiDaten,0,sizeof(int)*pImg->m_iW*pImg->m_iH);

	for(int iFolie=0; iFolie<GetTofConfig().GetFoilCount(); ++iFolie)
		for(int iZ0=0; iZ0<GetTofConfig().GetImagesPerFoil(); ++iZ0)
			for(int iY=0; iY<GetTofConfig().GetImageHeight(); ++iY)
				for(int iX=0; iX<GetTofConfig().GetImageWidth(); ++iX)
					pImg->m_puiDaten[iY*GetTofConfig().GetImageWidth()+iX] +=
													GetData(iFolie,iZ0,iX,iY);
}

// Alle Folien, die in iBits als aktiv markiert sind, addieren;
// dasselbe fuer die Kanaele
void TofImage::AddFoils(int iBits, int iZeitKanaeleBits, TmpImage *pImg) const
{
	if(!pImg) return;

	bool bFolieAktiv[GetTofConfig().GetFoilCount()],
		bKanaeleAktiv[GetTofConfig().GetImagesPerFoil()];

	for(int i=0; i<GetTofConfig().GetFoilCount(); ++i)
	{
		if(iBits & (1<<i)) bFolieAktiv[i]=true;
		else bFolieAktiv[i]=false;
	}

	for(int i=0; i<GetTofConfig().GetImagesPerFoil(); ++i)
	{
		if(iZeitKanaeleBits & (1<<i)) bKanaeleAktiv[i]=true;
		else bKanaeleAktiv[i]=false;
	}

	unsigned int uiAusgabe[GetTofConfig().GetImageHeight()]
						  [GetTofConfig().GetImageWidth()];
	memset(uiAusgabe,0,GetTofConfig().GetImageHeight()*
					   GetTofConfig().GetImageWidth()*sizeof(int));

	unsigned int *puiWave = new unsigned int[GetTofConfig().GetImageWidth()*
											GetTofConfig().GetImageHeight()];
	if(puiWave==NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line "
			   << __LINE__ << ")!\n";
		return;
	}

	pImg->Clear();
	pImg->m_iW = GetTofConfig().GetImageWidth();
	pImg->m_iH = GetTofConfig().GetImageHeight();
	pImg->m_puiDaten = puiWave;

	for(int iFolie=0; iFolie<GetTofConfig().GetFoilCount(); ++iFolie)
	{
		if(!bFolieAktiv[iFolie]) continue;

		for(int iZ0=0; iZ0<GetTofConfig().GetImagesPerFoil(); ++iZ0)
		{
			if (!bKanaeleAktiv[iZ0]) continue;
			for(int iY=0; iY<GetTofConfig().GetImageHeight(); ++iY)
				for(int iX=0; iX<GetTofConfig().GetImageWidth(); ++iX)
					uiAusgabe[iY][iX] += GetData(iFolie,iZ0,iX,iY);
		}
	}

	for(int iY=0; iY<GetTofConfig().GetImageHeight(); ++iY)
		for(int iX=0; iX<GetTofConfig().GetImageWidth(); ++iX)
				puiWave[iY*GetTofConfig().GetImageWidth()+iX] =
															uiAusgabe[iY][iX];
}

// Alle Kanaele, die im bool-Feld gesetzt sind, addieren
void TofImage::AddFoils(const bool *pbKanaele, TmpImage *pImg) const
{
	if(!pImg) return;

	unsigned int uiAusgabe[GetTofConfig().GetImageHeight()]
						  [GetTofConfig().GetImageWidth()];
	memset(uiAusgabe, 0, GetTofConfig().GetImageHeight()*
						 GetTofConfig().GetImageWidth()*sizeof(int));

	unsigned int *puiWave = new unsigned int[GetTofConfig().GetImageWidth()*
											 GetTofConfig().GetImageHeight()];
	if(puiWave==NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line "
			   << __LINE__ << ")!\n";
		return;
	}

	pImg->Clear();
	pImg->m_iW = GetTofConfig().GetImageWidth();
	pImg->m_iH = GetTofConfig().GetImageHeight();
	pImg->m_puiDaten = puiWave;

	for(int iFolie=0; iFolie<GetTofConfig().GetFoilCount(); ++iFolie)
	{
		for(int iZ0=0; iZ0<GetTofConfig().GetImagesPerFoil(); ++iZ0)
		{
			if(!pbKanaele[iFolie*GetTofConfig().GetImagesPerFoil() + iZ0])
				continue;

			for(int iY=0; iY<GetTofConfig().GetImageHeight(); ++iY)
				for(int iX=0; iX<GetTofConfig().GetImageWidth(); ++iX)
					uiAusgabe[iY][iX] += GetData(iFolie, iZ0, iX, iY);
		}
	}

	for(int iY=0; iY<GetTofConfig().GetImageHeight(); ++iY)
		for(int iX=0; iX<GetTofConfig().GetImageWidth(); ++iX)
				puiWave[iY*GetTofConfig().GetImageWidth()+iX] =
															uiAusgabe[iY][iX];
}

// Alle Phasenbilder, die im bool-Feld gesetzt sind, addieren
void TofImage::AddPhases(const bool *pbFolien, TmpImage *pImg) const
{
	if(pImg==NULL) return;
	double *pdWave = new double[GetTofConfig().GetImageWidth()*
								GetTofConfig().GetImageHeight()];
	if(pdWave==NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line "
			   << __LINE__ << ")!\n";
		return;
	}

	pImg->Clear();
	pImg->m_iW = GetTofConfig().GetImageWidth();
	pImg->m_iH = GetTofConfig().GetImageHeight();
	pImg->m_pdDaten = pdWave;

	memset(pdWave, 0, sizeof(double)*pImg->m_iW*pImg->m_iH);

	for(int iFolie=0; iFolie<GetTofConfig().GetFoilCount(); ++iFolie)
	{
		if(!pbFolien[iFolie]) continue;

		TmpImage tmpimg;
		GetPhaseGraph(iFolie, &tmpimg);

		pImg->Add(tmpimg);
	}

	for(int iY=0; iY<pImg->m_iH; ++iY)
		for(int iX=0; iX<pImg->m_iW; ++iX)
			pdWave[iY*pImg->m_iW + iX] = fmod(pdWave[iY*pImg->m_iW + iX], 360.);
}

// Alle Kontrastbilder, die im bool-Feld gesetzt sind, addieren
void TofImage::AddContrasts(const bool *pbFolien, TmpImage *pImg) const
{
	if(pImg==NULL) return;
	double *pdWave = new double[GetTofConfig().GetImageWidth()*
								GetTofConfig().GetImageHeight()];
	if(pdWave==NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line "
			   << __LINE__ << ")!\n";
		return;
	}

	pImg->Clear();
	pImg->m_iW = GetTofConfig().GetImageWidth();
	pImg->m_iH = GetTofConfig().GetImageHeight();
	pImg->m_pdDaten = pdWave;

	memset(pdWave, 0, sizeof(double)*pImg->m_iW*pImg->m_iH);

	for(int iFolie=0; iFolie<GetTofConfig().GetFoilCount(); ++iFolie)
	{
		if(!pbFolien[iFolie]) continue;

		TmpImage tmpimg;
		GetContrastGraph(iFolie, &tmpimg);

		pImg->Add(tmpimg);
	}
}

// Für Kalibrierungsdiagramm
void TofImage::GetPhaseGraph(int iFolie, TmpImage *pImg, bool bInDeg) const
{
	if(pImg==NULL) return;

	int iStartX = 0,
		iStartY = 0,
		iEndX = GetTofConfig().GetImageWidth(),
		iEndY = GetTofConfig().GetImageHeight();

	GetTofConfig().CheckTofArguments(&iStartX, &iEndX, &iStartY, &iEndY);

	pImg->Clear();
	pImg->m_iW = abs(iEndX-iStartX);
	pImg->m_iH = abs(iEndY-iStartY);

	const int XSIZE = GlobalConfig::iPhaseBlockSize[0],
			  YSIZE = GlobalConfig::iPhaseBlockSize[1];

	double *pdWave = new double[(pImg->m_iW+XSIZE) * (pImg->m_iH+YSIZE)];
	if(pdWave==NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line "
			   << __LINE__ << ")!\n";
		return;
	}
	pImg->m_pdDaten = pdWave;

	for(int iY=iStartY; iY<iEndY; iY+=YSIZE)
		for(int iX=iStartX; iX<iEndX; iX+=XSIZE)
		{
			TmpGraph tmpGraph;
			GetGraph(iX, iX+XSIZE, iY, iY+YSIZE, iFolie, &tmpGraph);

			double dPhase, dFreq, dAmp, dOffs;
			bool bFitValid = tmpGraph.FitSinus(dPhase, dFreq, dAmp, dOffs);

			if(!bFitValid || dPhase!=dPhase)
				dPhase = 0.;

			if(bInDeg) dPhase = dPhase*180./M_PI;

			for(int i=0; i<YSIZE; ++i)
				for(int j=0; j<XSIZE; ++j)
					pdWave[(iY-iStartY+i)*pImg->m_iW+(iX-iStartX+j)] = dPhase;
		}
}

void TofImage::GetContrastGraph(int iFoil, TmpImage *pImg) const
{
	if(pImg==NULL) return;

	int iStartX = 0,
		iStartY = 0,
		iEndX = GetTofConfig().GetImageWidth(),
		iEndY = GetTofConfig().GetImageHeight();

	GetTofConfig().CheckTofArguments(&iStartX, &iEndX, &iStartY, &iEndY);

	pImg->Clear();
	pImg->m_iW = iEndX-iStartX;
	pImg->m_iH = iEndY-iStartY;

	const int XSIZE = GlobalConfig::iContrastBlockSize[0],
		  YSIZE = GlobalConfig::iContrastBlockSize[1];

	double *pdWave = new double[(pImg->m_iW+XSIZE) * (pImg->m_iH+YSIZE)];
	if(pdWave==NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line "
			   << __LINE__ << ")!\n";
		return;
	}
	pImg->m_pdDaten = pdWave;

	for(int iY=iStartY; iY<iEndY; iY+=YSIZE)
		for(int iX=iStartX; iX<iEndX; iX+=XSIZE)
		{
			TmpGraph tmpGraph;
			GetGraph(iX, iX+XSIZE, iY, iY+YSIZE, iFoil, &tmpGraph);

			double dPhase, dFreq, dAmp, dOffs;
			bool bFitValid = tmpGraph.FitSinus(dPhase, dFreq, dAmp, dOffs);

			double dContrast = fabs(dAmp/dOffs);
			if(!bFitValid || dContrast!=dContrast)
				dContrast = 0.;

			for(int i=0; i<YSIZE; ++i)
				for(int j=0; j<XSIZE; ++j)
					pdWave[(iY-iStartY+i)*pImg->m_iW+(iX-iStartX+j)]=dContrast;
		}
}

unsigned int TofImage::GetCounts() const
{
	TmpImage img;
	GetOverview(&img);

	unsigned int uiCnt = 0;
	for(int iY=0; iY<GetTofConfig().GetImageHeight(); ++iY)
		for(int iX=0; iX<GetTofConfig().GetImageWidth(); ++iX)
		{
			if(m_bUseRoi && m_roi.IsInside(iX, iY))
				uiCnt += img.GetData(iX, iY);
		}
	return uiCnt;
}

unsigned int TofImage::GetCounts(int iStartX, int iEndX,
								 int iStartY, int iEndY) const
{
	GetTofConfig().CheckTofArguments(&iStartX, &iEndX, &iStartY, &iEndY);

	TmpImage img;
	GetOverview(&img);

	unsigned int uiCnt = 0;
	for(int iY=iStartY; iY<iEndY; ++iY)
		for(int iX=iStartX; iX<iEndX; ++iX)
			uiCnt += img.GetData(iX, iY);

	return uiCnt;
}

// *****************************************************************************

TmpImage TofImage::GetROI(int iStartX, int iEndX, int iStartY, int iEndY,
						  int iFolie, int iZ) const
{
	TmpImage img;
	GetROI(iStartX, iEndX, iStartY, iEndY, iFolie, iZ, &img);
	return img;
}

TmpGraph TofImage::GetGraph(int iStartX, int iEndX, int iStartY, int iEndY,
						    int iFoil) const
{
	TmpGraph graph;
	GetGraph(iStartX, iEndX, iStartY, iEndY, iFoil, &graph);
	return graph;
}

TmpGraph TofImage::GetGraph(int iFoil) const
{
	TmpGraph graph;
	GetGraph(iFoil, &graph);
	return graph;
}

TmpGraph TofImage::GetTotalGraph(int iStartX, int iEndX, int iStartY, int iEndY,
								 double dPhaseShift) const
{
	TmpGraph graph;
	GetTotalGraph(iStartX, iEndX, iStartY, iEndY, dPhaseShift, &graph);
	return graph;
}

TmpImage TofImage::GetOverview() const
{
	TmpImage img;
	GetOverview(&img);
	return img;
}

TmpImage TofImage::GetPhaseGraph(int iFolie, bool bInDeg) const
{
	TmpImage img;
	GetPhaseGraph(iFolie, &img, bInDeg);
	return img;
}

TmpImage TofImage::GetContrastGraph(int iFolie) const
{
	TmpImage img;
	GetContrastGraph(iFolie, &img);
	return img;
}

TmpImage TofImage::AddFoils(const bool *pbKanaele) const
{
	TmpImage img;
	AddFoils(pbKanaele, &img);
	return img;
}

TmpImage TofImage::AddPhases(const bool *pbFolien) const
{
	TmpImage img;
	AddPhases(pbFolien, &img);
	return img;
}

TmpImage TofImage::AddContrasts(const bool *pbFolien) const
{
	TmpImage img;
	AddContrasts(pbFolien, &img);
	return img;
}
// **************** TOF ********************************************************



// **************** PAD ********************************************************
PadImage::PadImage(const char *pcFileName, bool bExternalMem,
				   const PadConfig* conf)
		: m_iMin(0),m_iMax(0), m_bExternalMem(bExternalMem)
{
	m_puiDaten = 0;
	m_bUseRoi = false;

	if(conf)
		m_config = *conf;
	else
		m_config = (PadConfig)GlobalConfig::GetTofConfig();

	logger.SetCurLogLevel(LOGLEVEL_INFO);
	logger << "Loader: New PAD image: " << "external mem=" << m_bExternalMem
			  << ", width=" << GetWidth()
			  << ", height=" << GetHeight() << ".\n";

	if(!m_bExternalMem)
	{
		m_puiDaten = new unsigned int[GetPadSize()];
		if(m_puiDaten==NULL)
		{
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "Loader: Could not allocate memory (line "
				   << __LINE__ << ")!\n";
			return;
		}

		if(pcFileName)
			LoadFile(pcFileName);
		else
			memset(m_puiDaten,0,GetPadSize()*sizeof(int));
	}
}

PadImage::PadImage(const PadImage& pad) : m_bExternalMem(false)
{
	m_iMin=pad.m_iMin;
	m_iMax=pad.m_iMax;

	m_config = pad.m_config;

	m_bUseRoi = pad.m_bUseRoi;
	m_roi = pad.m_roi;

	m_puiDaten = new unsigned int[GetPadSize()];
	if(m_puiDaten == NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line "
			   << __LINE__ << ")!\n";
		return;
	}
	memcpy(m_puiDaten, pad.m_puiDaten, sizeof(int)*GetPadSize());
}

PadImage::~PadImage()
{
	Clear();
}

void PadImage::Clear()
{
	if(m_puiDaten && !m_bExternalMem)
	{
		delete[] m_puiDaten;
		m_puiDaten=0;
	}
}

int PadImage::GetWidth() const
{
	return GetPadConfig().GetImageWidth();
}

int PadImage::GetHeight() const
{
	return GetPadConfig().GetImageHeight();
}

int PadImage::GetPadSize() const
{
	return GetHeight()*GetWidth();
}

const PadConfig& PadImage::GetPadConfig() const
{
	return m_config;
}

void PadImage::SetExternalMem(void* pvDaten)
{
	if(!m_bExternalMem)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: This PAD does not use external memory"
				  " (line " << __LINE__ << ")!\n";
		return;
	}

	m_puiDaten = (unsigned int*)pvDaten;
	//UpdateRange();
}

void PadImage::UpdateRange()
{
	m_iMin=std::numeric_limits<int>::max();
	m_iMax=0;
	for(int iY=0; iY<GetPadConfig().GetImageHeight(); ++iY)
	{
		for(int iX=0; iX<GetPadConfig().GetImageWidth(); ++iX)
		{
			int iDat = int(GetData(iX,iY));

			m_iMin = (m_iMin<iDat) ? m_iMin : iDat;
			m_iMax = (m_iMax>iDat) ? m_iMax : iDat;
		}
	}
}

double PadImage::GetDoubleMin() const { return double(GetIntMin()); }
double PadImage::GetDoubleMax() const { return double(GetIntMax()); }
int PadImage::GetIntMin() const { return m_iMin; }
int PadImage::GetIntMax() const { return m_iMax; }

int PadImage::LoadMem(const unsigned int *puiBuf, unsigned int uiBufLen)
{
	if(m_bExternalMem)
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "Loader: This PAD uses external memory"
				  " (line " << __LINE__ << ")!\n";
	}

	if(uiBufLen!=(unsigned int)GetPadConfig().GetImageHeight()*
							   GetPadConfig().GetImageWidth())
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Buffer size (" << uiBufLen << " ints) != PAD size ("
			   << GetPadConfig().GetImageHeight()*
			      GetPadConfig().GetImageWidth()
			   << " ints)." << "\n";
		return LOAD_SIZE_MISMATCH;
	}

	memcpy(m_puiDaten, puiBuf, sizeof(int)*GetPadConfig().GetImageHeight()*
										   GetPadConfig().GetImageWidth());

	// falls PowerPC, ints von little zu big endian konvertieren
#ifdef __BIG_ENDIAN__
		for(int iY=0; iY<GetPadConfig().GetImageHeight(); ++iY)
			for(int iX=0; iX<GetPadConfig().GetImageWidth(); ++iX)
				GetData(iX,iY) = endian_swap(GetData(iX,iY));
#endif

	UpdateRange();
	return LOAD_SUCCESS;
}

int PadImage::SaveFile(const char *pcFileName)
{
	FILE *pf = fopen(pcFileName, "wb");
	if(!pf)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not open file \"" << pcFileName
			   << "\" for writing."
			   << "\n";
		return SAVE_FAIL;
	}

	unsigned int uiLen = fwrite(m_puiDaten, sizeof(unsigned int),
		   GetPadConfig().GetImageHeight()*GetPadConfig().GetImageWidth(), pf);

	int iRet = SAVE_SUCCESS;
	if(uiLen != (unsigned int)(GetPadConfig().GetImageHeight()*
							   GetPadConfig().GetImageWidth()))
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not write file \"" << pcFileName << "\"."
			   << "\n";
		iRet = SAVE_FAIL;
	}

	fclose(pf);
	return iRet;
}

int PadImage::LoadFile(const char *pcFileName)
{
	if(m_bExternalMem)
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "Loader: This PAD uses external memory"
				  " (line " << __LINE__ << ")!\n";
	}

	int iRet = LOAD_SUCCESS;

	FILE *pf = fopen(pcFileName,"rb");
	if(!pf)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not open file \"" << pcFileName << "\"."
			   << "\n";
		return LOAD_FAIL;
	}

	unsigned int uiBufLen = fread(m_puiDaten, sizeof(unsigned int),
								GetPadConfig().GetImageHeight()*
								GetPadConfig().GetImageWidth(), pf);
	if(!uiBufLen)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not read file \"" << pcFileName << "\"."
			   << "\n";
	}

	if(uiBufLen != (unsigned int)GetPadConfig().GetImageHeight()*
								 GetPadConfig().GetImageWidth())
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Buffer size (" << uiBufLen << " ints) != PAD size ("
			   << GetPadConfig().GetImageHeight()*
				  GetPadConfig().GetImageWidth() << " ints)."
			   << "\n";
		iRet = LOAD_SIZE_MISMATCH;
	}
	fclose(pf);

// falls PowerPC, ints von little zu big endian konvertieren
#ifdef __BIG_ENDIAN__
	for(int iY=0; iY<GetPadConfig().GetImageHeight(); ++iY)
		for(int iX=0; iX<GetPadConfig().GetImageWidth(); ++iX)
			GetData(iX,iY) = endian_swap(GetData(iX,iY));
#endif

	UpdateRange();
	return iRet;
}


void PadImage::Print(const char* pcOutFile)
{
	std::ostream* fOut = &std::cout;
	if(pcOutFile)
		fOut = new std::ofstream(pcOutFile);

	for(int iY=0; iY<GetPadConfig().GetImageHeight(); ++iY)
	{
		for(int iX=0; iX<GetPadConfig().GetImageWidth(); ++iX)
				(*fOut) << GetData(iX,iY) << "\t";
		(*fOut) << "\n";
	}

	(*fOut) << std::endl;
	if(pcOutFile)
	{
		((std::ofstream*)fOut)->close();
		delete fOut;
	}
}

unsigned int* PadImage::GetRawData(void)
{
	return m_puiDaten;
}

unsigned int PadImage::GetData(int iX, int iY) const
{
	return GetIntData(iX, iY);
}

unsigned int PadImage::GetDataInsideROI(int iX, int iY) const
{
	if(m_bUseRoi)
	{
		// only continue if point is in ROI
		if(!m_roi.IsInside(iX, iY))
			return 0;
	}

	return GetData(iX, iY);
}

double PadImage::GetDoubleData(int iX, int iY) const
{
	return double(GetIntData(iX, iY));
}

unsigned int PadImage::GetIntData(int iX, int iY) const
{
	if(m_puiDaten==NULL) return 0;

	if(iX>=0 && iX<GetPadConfig().GetImageWidth() &&
	   iY>=0 && iY<GetPadConfig().GetImageHeight())
		return m_puiDaten[iY*GetPadConfig().GetImageWidth() + iX];
	else
		return 0;
}

unsigned int PadImage::GetCounts() const
{
	unsigned int uiCnt = 0;
	for(int iY=0; iY<GetPadConfig().GetImageHeight(); ++iY)
		for(int iX=0; iX<GetPadConfig().GetImageWidth(); ++iX)
			uiCnt += GetDataInsideROI(iX, iY);

	return uiCnt;
}

unsigned int PadImage::GetCounts(int iStartX, int iEndX,
								 int iStartY, int iEndY) const
{
	GetPadConfig().CheckPadArguments(&iStartX, &iEndX, &iStartY, &iEndY);

	unsigned int uiCnt = 0;
	for(int iY=iStartY; iY<iEndY; ++iY)
		for(int iX=iStartX; iX<iEndX; ++iX)
			uiCnt += GetData(iX, iY);
	return uiCnt;
}

void PadImage::UseRoi(bool bUseRoi) { m_bUseRoi = bUseRoi; }
Roi& PadImage::GetRoi() { return m_roi; }
bool PadImage::GetUseRoi() const { return m_bUseRoi; };
// *************** PAD *********************************************************



// *************** TmpImage ****************************************************
TmpImage::TmpImage() : m_iW(GlobalConfig::GetTofConfig().GetImageWidth()),
					   m_iH(GlobalConfig::GetTofConfig().GetImageHeight()),
					   m_puiDaten(NULL), m_pdDaten(NULL),
					   m_dMin(0), m_dMax(0)
{}

TmpImage::TmpImage(const TmpImage& tmp)
{
	m_iW = tmp.m_iW;
	m_iH = tmp.m_iH;
	m_dMin = tmp.m_dMin;
	m_dMax = tmp.m_dMax;
	m_puiDaten = NULL;
	m_pdDaten = NULL;

	if(tmp.m_puiDaten)
	{
		m_puiDaten = new unsigned int[m_iW*m_iH];
		if(m_puiDaten==NULL)
		{
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "Loader: Could not allocate memory (line "
				   << __LINE__ << ")!\n";
			return;
		}
		memcpy(m_puiDaten,tmp.m_puiDaten,sizeof(int)*m_iW*m_iH);
	}
	if(tmp.m_pdDaten)
	{
		m_pdDaten = new double[m_iW*m_iH];
		if(m_pdDaten==NULL)
		{
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "Loader: Could not allocate memory (line "
				   << __LINE__ << ")!\n";
			return;
		}
		memcpy(m_pdDaten,tmp.m_pdDaten,sizeof(double)*m_iW*m_iH);
	}
}

void TmpImage::Clear(void)
{
	if(m_puiDaten)
	{
		delete[] m_puiDaten;
		m_puiDaten=NULL;
	}
	if(m_pdDaten)
	{
		delete[] m_pdDaten;
		m_pdDaten=NULL;
	}
}

TmpImage::~TmpImage()
{
	Clear();
}

double TmpImage::GetData(int iX, int iY) const
{
	return GetDoubleData(iX, iY);
}

unsigned int TmpImage::GetIntData(int iX, int iY) const
{
	if(iX>=0 && iX<m_iW && iY>=0 && iY<m_iH)
	{
		if(m_puiDaten)
			return m_puiDaten[iY*m_iW + iX];
		else if(m_pdDaten)
			return (unsigned int)(m_pdDaten[iY*m_iW + iX]);
	}
	return 0;
}

double TmpImage::GetDoubleData(int iX, int iY) const
{
	if(iX>=0 && iX<m_iW && iY>=0 && iY<m_iH)
	{
		if(m_puiDaten)
			return double(m_puiDaten[iY*m_iW + iX]);
		else if(m_pdDaten)
			return m_pdDaten[iY*m_iW + iX];
	}
	return 0.;
}

int TmpImage::GetWidth() const { return m_iW; }
int TmpImage::GetHeight() const { return m_iH; }

void TmpImage::Add(const TmpImage& tmp)
{
	if(this->m_iH!=tmp.m_iH || this->m_iW!=tmp.m_iW)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Trying to sum incompatible images"
				  " (line " << __LINE__ << ")!\n";
		return;
	}

	for(int iY=0; iY<m_iH; ++iY)
	{
		for(int iX=0; iX<m_iW; ++iX)
		{
			if(m_puiDaten)
			{
				m_puiDaten[iY*m_iW + iX] += (unsigned int)tmp.GetData(iX,iY);
			}
			else if(m_pdDaten)
			{
				m_pdDaten[iY*m_iW + iX] += tmp.GetData(iX,iY);
			}
		}
	}
}

void TmpImage::UpdateRange()
{
	if(!m_puiDaten && !m_pdDaten) return;

	m_dMin=std::numeric_limits<double>::max();
	m_dMax=0;
	for(int iY=0; iY<m_iH; ++iY)
	{
		for(int iX=0; iX<m_iW; ++iX)
		{
			if(m_puiDaten)
			{
				m_dMin = (m_dMin<m_puiDaten[m_iW*iY+iX])
							? m_dMin
							: m_puiDaten[m_iW*iY+iX];
				m_dMax = (m_dMax>m_puiDaten[m_iW*iY+iX])
							? m_dMax
							: m_puiDaten[m_iW*iY+iX];
			}
			else if(m_pdDaten)
			{
				m_dMin = (m_dMin<m_pdDaten[m_iW*iY+iX])
							? m_dMin
							: m_pdDaten[m_iW*iY+iX];
				m_dMax = (m_dMax>m_pdDaten[m_iW*iY+iX])
							? m_dMax
							: m_pdDaten[m_iW*iY+iX];
			}
		}
	}
}

int TmpImage::GetIntMin(void) const { return int(GetDoubleMin()); }
int TmpImage::GetIntMax(void) const { return int(GetDoubleMax()); }
double TmpImage::GetDoubleMin(void) const { return m_dMin; }
double TmpImage::GetDoubleMax(void) const { return m_dMax; }

bool TmpImage::WriteXML(const char* pcFileName) const
{
	std::ofstream ofstr(pcFileName);
	if(!ofstr.is_open())
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not open file \""
			   << pcFileName << "\" for writing.\n";
		return false;
	}

	ofstr << "<measurement_file>\n";
	ofstr << "<instrument_name>MIRA</instrument_name>\n";
	ofstr << "<location>Forschungsreaktor Muenchen II - FRM2</location>\n";

	int iRes = 1024;

	ofstr << "<measurement_data>\n";
	ofstr << "<resolution>" << iRes << "</resolution>\n";
	ofstr << "<detector_value>\n";

	if(iRes % m_iW || iRes % m_iH)
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "Loader: Resolution does not match.\n";
	}

	for(int iX=0; iX<m_iW; ++iX)
	{
		for (int t1=0; t1 < iRes/m_iW; ++t1)
		{
			for(int iY=0; iY<m_iH; ++iY)
			{
				for (int t2=0; t2 < iRes/m_iH; ++t2)
					ofstr << GetIntData(iX,iY) << " ";
			}
			ofstr << "\n";
		}
	}

	ofstr << "</detector_value>\n";
	ofstr << "</measurement_data>\n";

	ofstr << "</measurement_file>\n";
	ofstr.close();
	return true;
}

// PAD-Image zu TmpImg konvertieren
void TmpImage::ConvertPAD(PadImage* pPad)
{
	m_iW = pPad->GetPadConfig().GetImageWidth();
	m_iH = pPad->GetPadConfig().GetImageHeight();
	m_dMin = pPad->m_iMin;
	m_dMax = pPad->m_iMax;

	m_puiDaten = new unsigned int[m_iW*m_iH];
	if(m_puiDaten==NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line "
			   << __LINE__ << ")!\n";
		return;
	}
	memcpy(m_puiDaten, pPad->m_puiDaten, m_iW*m_iH*sizeof(int));
}


// ********************** TmpGraph *********************************************

TmpGraph::TmpGraph() : m_iW(0), m_puiDaten(0)
{}

TmpGraph::~TmpGraph()
{
	if(m_puiDaten)
	{
		delete[] m_puiDaten;
		m_puiDaten=NULL;
	}
}

unsigned int TmpGraph::GetData(int iX) const
{
	if(!m_puiDaten) return 0;
	if(iX>=0 && iX<m_iW)
		return m_puiDaten[iX];
	return 0;
}

int TmpGraph::GetWidth(void) const { return m_iW; }

int TmpGraph::GetMin() const
{
	if(!m_puiDaten) return 0;

	unsigned int uiMin = std::numeric_limits<int>::max();
	for(int i=0; i<m_iW; ++i)
		if(m_puiDaten[i]<uiMin) uiMin = m_puiDaten[i];
	return uiMin;
}

int TmpGraph::GetMax() const
{
	if(!m_puiDaten) return 0;

	unsigned int uiMax = 0;
	for(int i=0; i<m_iW; ++i)
		if(m_puiDaten[i]>uiMax) uiMax = m_puiDaten[i];
	return uiMax;
}

bool TmpGraph::IsLowerThan(int iTotal) const
{
	int iSum=0;
	for(int i=0; i<m_iW; ++i)
		iSum += GetData(i);

	return iSum < iTotal;
}

#ifdef USE_MINUIT
// ************************** Zeug für Minuit **********************************
// Modellfunktion für sin-Fit
class Sinus : public ROOT::Minuit2::FCNBase
{
	protected:
		double *m_pdy;			// experimentelle Werte
 		double *m_pddy;			// Standardabweichungen
		int m_iNum;				// Anzahl der Werte

	public:
		Sinus() : m_pdy(NULL), m_pddy(NULL), m_iNum(0)
		{}

		void Clear(void)
		{
			if(m_pddy) { delete[] m_pddy; m_pddy=NULL; }
			if(m_pdy) { delete[] m_pdy; m_pdy=NULL; }
			m_iNum=0;
		}

		virtual ~Sinus()
		{
			Clear();
		}

		double chi2(const std::vector<double>& params) const
		{
			double dphase = params[0];
			double damp = params[1];
			double doffs = params[2];
			double dscale = 2.*M_PI/double(m_iNum);

			// force non-negative amplitude parameter
			if(damp<0.) return std::numeric_limits<double>::max();

			double dchi2 = 0.;
			for(int i=0; i<m_iNum; ++i)
			{
				double dAbweichung = m_pddy[i];

				// prevent division by zero
				if(fabs(dAbweichung) < std::numeric_limits<double>::epsilon())
					dAbweichung = std::numeric_limits<double>::epsilon();

				double d = (m_pdy[i] - (damp*sin(double(i)*dscale +
										dphase)+doffs)) / dAbweichung;
				dchi2 += d*d;
			}
			return dchi2;
		}

		double operator()(const std::vector<double>& params) const
		{
			return chi2(params);
		}

		double Up() const
		{ return 1.; }

		const double* GetValues() const
		{ return m_pdy; }

		const double* GetDeviations() const
		{ return m_pddy; }

		void SetValues(int iSize, const double* pdy)
		{
			Clear();
			m_iNum = iSize;
			m_pdy = new double[iSize];
			m_pddy = new double[iSize];

			for(int i=0; i<iSize; ++i)
			{
				m_pdy[i] = pdy[i];			// Wert
				m_pddy[i] = sqrt(m_pdy[i]);	// Fehler
			}
		}

		void SetValues(int iSize, const unsigned int* piy)
		{
			Clear();
			m_iNum = iSize;
			m_pdy = new double[iSize];
			m_pddy = new double[iSize];

			for(int i=0; i<iSize; ++i)
			{
				m_pdy[i] = double(piy[i]);	// Wert
				m_pddy[i] = sqrt(m_pdy[i]);	// Fehler
			}
		}
};

bool TmpGraph::FitSinus(double &dPhase, double &dScale,
						double &dAmp, double &dOffs) const
{
	if(m_iW<=0) return false;

	// Scale-Parameter fix
	dScale = 2.*M_PI/double(m_iW);

	double dMaxVal=GetMax(), dMinVal=GetMin();
	dOffs = dMinVal + (dMaxVal-dMinVal)/2.;		// Hint-Werte
	dAmp = (dMaxVal-dMinVal)/2.;				// Hint-Werte

	if(IsLowerThan(1))
	{
		dPhase=0.;
		return false;
	}

	Sinus fkt;
	fkt.SetValues(m_iW, m_puiDaten);

	ROOT::Minuit2::MnUserParameters upar;
	upar.Add("phase", M_PI, 0.01);
	upar.Add("amp", dAmp, sqrt(dAmp));
	upar.Add("offset", dOffs, sqrt(dOffs));
	//upar.Add("scale", 2.*M_PI/16., 0.1);		// kein Fit-Parameter

	ROOT::Minuit2::MnApplication *pMinimize = 0;

	unsigned int uiStrategy = GlobalConfig::GetMinuitStrategy();
	switch(GlobalConfig::GetMinuitAlgo())
	{
		case MINUIT_SIMPLEX:
			pMinimize = new ROOT::Minuit2::MnSimplex(fkt, upar, uiStrategy);
			break;

		case MINUIT_MINIMIZE:
			pMinimize = new ROOT::Minuit2::MnMinimize(fkt, upar, uiStrategy);
			break;

		default:
		case MINUIT_MIGRAD:
			pMinimize = new ROOT::Minuit2::MnMigrad(fkt, upar, uiStrategy);
			break;
	}

	ROOT::Minuit2::FunctionMinimum mini = (*pMinimize)(
									GlobalConfig::GetMinuitMaxFcn(),
									GlobalConfig::GetMinuitTolerance());
	delete pMinimize;
	pMinimize = 0;

	dPhase = mini.Parameters().Vec()[0];
	dAmp = mini.Parameters().Vec()[1];
	dOffs = mini.Parameters().Vec()[2];
	//dScale = mini.Parameters().Vec()[3];

	// Phasen auf 0..2*Pi einschränken
	dPhase = fmod(dPhase, 2.*M_PI);
	if(dPhase<0.) dPhase += 2.*M_PI;

	if(!mini.IsValid())
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Invalid fit." << "\n";
		return false;
	}

	// check for NaN
	if(dPhase!=dPhase || dAmp!=dAmp || dOffs!=dOffs)
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "Loader: Incorrect fit." << "\n";
		return false;
	}
	return true;
}
// *****************************************************************************
#else
bool TmpGraph::FitSinus(double &dPhase, double &dScale,
						double &dAmp, double &dOffs) const
{
	logger.SetCurLogLevel(LOGLEVEL_ERR);
	logger << "Loader: Not compiled with minuit." << "\n";
	return false;
}
#endif //USE_MINUIT
