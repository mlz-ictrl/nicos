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
// Klassen zum Laden und Verarbeiten von Tof-Dateien

#include "tofloader.h"

#include <fstream>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <vector>
#include <string.h>
#include <limits>
#include <iomanip>

#include "../aux/logger.h"
#include "../aux/helper.h"
#include "../aux/fit.h"
#include "../aux/gc.h"
#include "../aux/fourier.h"

#include "tofloader_graph.cpp"
#include "tofloader_image.cpp"


//------------------------------------------------------------------------------
typedef bool (Fourier::*t_corrfkt)(double, const double*, double *, double);

static t_corrfkt get_correction_fkt(int iShiftMeth)
{
	if(iShiftMeth == SHIFT_SINE_ONLY)
		return &Fourier::shift_sin;
	else if(iShiftMeth == SHIFT_ZERO_ORDER)
		return &Fourier::phase_correction_0;
	else
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Unknown phase-correction method selected.\n";
	}
	return 0;
}
//------------------------------------------------------------------------------


//------------------------------------------------------------------------------
// TOF
TofImage::TofImage(const char *pcFileName,
				   bool bExternalMem, const TofConfig* conf)
		: m_puiDaten(0),
		  m_bExternalMem(bExternalMem),
		  m_bUseRoi(false),
		  m_bOk(false)
{
	if(conf)	// use given config
		m_config = *conf;
	else 		// if no config is given, copy global one
		m_config = GlobalConfig::GetTofConfig();

	logger.SetCurLogLevel(LOGLEVEL_INFO);
	logger << "Loader: New TOF image: " << "external mem=" << m_bExternalMem
			  << ", width=" << GetTofConfig().GetImageWidth()
			  << ", height=" << GetTofConfig().GetImageHeight()
			  << ", images=" << GetTofConfig().GetImageCount()
			  << ", comp=" << GetTofConfig().GetPseudoCompression()
			  << ".\n";

	// should TofImage manage its own memory?
	if(!m_bExternalMem)
	{
		int iSize = GetTofSize();
		m_puiDaten = (unsigned int*)gc.malloc(sizeof(int)*iSize, "tof_image");
		if(m_puiDaten==NULL)
		{
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "Loader: Could not allocate memory (line "
				   << __LINE__ << ")!\n";
			return;
		}

		if(pcFileName)
			m_bOk = (LoadFile(pcFileName) == LOAD_SUCCESS);
		else
			memset(m_puiDaten,0,iSize*sizeof(int));
	}
}

TofImage::~TofImage() { Clear(); }

TofImage* TofImage::copy() const
{
	TofImage *pTof = new TofImage(0, false, &m_config);
	
	pTof->m_bExternalMem = false;
	//pTof->m_config = m_config;
	pTof->m_roi = m_roi;
	pTof->m_bUseRoi = m_bUseRoi;
	pTof->m_bOk = m_bOk;

	/*
	for(int iFoil=0; iFoil<GetTofConfig().GetFoilCount(); ++iFoil)
		for(int iTc0=0; iTc<GetTofConfig().GetImagesPerFoil(); ++iTc)
			for(int iX=0; iX<GetTofConfig().GetImageWidth(); ++iX)
				for(int iY=0; iY<GetTofConfig().GetImageHeight(); ++iY)
				{
					unsigned int uiData = GetData(iFoil, iTc, iX, iY);
					pTof->SetData(iFoil, iTc, iX, iY, uiData);
				}
	*/

	memcpy(pTof->m_puiDaten, m_puiDaten, sizeof(int)*GetTofSize());
	return pTof;
}

bool TofImage::IsOk() const { return m_bOk; }

void TofImage::UseRoi(bool bUseRoi) { m_bUseRoi = bUseRoi; }
Roi& TofImage::GetRoi() { return m_roi; }
bool TofImage::GetUseRoi() const { return m_bUseRoi; };
const TofConfig& TofImage::GetTofConfig() const { return m_config; }

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
	bool bPseudoCompressed = GetTofConfig().GetPseudoCompression();

	int iSize = bPseudoCompressed
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
		gc.release(m_puiDaten);
		m_puiDaten=NULL;
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
	if(!GetTofConfig().GetPseudoCompression())
	{
		int iZ = GetTofConfig().GetFoilBegin(iFoil) + iTimechannel;

		if(GetTofConfig().GetSumFirstAndLast())
		{
			if(iTimechannel!=0)
				return GetData(iZ,iX,iY);
			else
				return GetData(iZ,iX,iY)+
					   GetData(iZ+GetTofConfig().GetImagesPerFoil(), iX, iY);
		}
		else
		{
			return GetData(iZ,iX,iY);
		}
	}
	else
	{
		return GetData(iFoil*GetTofConfig().GetImagesPerFoil()
						+ iTimechannel, iX, iY);
	}
}

void TofImage::SetData(int iImage, int iX, int iY, unsigned int uiCnt)
{
	if(m_puiDaten && iImage>=0 && iImage<GetTofConfig().GetImageCount() &&
			iX>=0 && iX<GetTofConfig().GetImageWidth() &&
			iY>=0 && iY<GetTofConfig().GetImageHeight())
	{
	   m_puiDaten[iImage*GetTofConfig().GetImageWidth()*
							    GetTofConfig().GetImageHeight() +
								iY*GetTofConfig().GetImageWidth() + iX] = uiCnt;
	}

}

void TofImage::SetData(int iFoil, int iTc, int iX, int iY, unsigned int uiCnt)
{
	if(!GetTofConfig().GetPseudoCompression())
	{
		int iZ = GetTofConfig().GetFoilBegin(iFoil) + iTc;
		SetData(iZ, iX, iY, uiCnt);
	}
	else
	{
		SetData(iFoil*GetTofConfig().GetImagesPerFoil()+iTc, iX, iY, uiCnt);
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

		//double dFractionInRoi = m_roi.HowMuchInside(iX, iY);
		//return double(GetData(iFoil, iTimechannel, iX, iY)) * dFractionInRoi;
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

		//double dFractionInRoi = m_roi.HowMuchInside(iX, iY);
		//return double(GetData(iImage, iX, iY)) * dFractionInRoi;
	}

	return GetData(iImage, iX, iY);
}

unsigned int* TofImage::GetRawData(void) const
{
	return m_puiDaten;
}

int TofImage::LoadMem(const char *strBuf, unsigned int istrBufLen)
{
	const unsigned int *puiBuf = (unsigned int *)strBuf;
	unsigned int uiBufLen = istrBufLen / 4;

	if(m_bExternalMem)
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "Loader: This TOF uses external memory"
				  " (line " << __LINE__ << ")!\n";
	}

	int iSize = GetTofSize();

	if(uiBufLen!=(unsigned int)iSize)
	{
		if(uiBufLen < (unsigned int)iSize)
		{
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "Loader: Buffer size (" << uiBufLen << " ints) != TOF size ("
				<< iSize << " ints)." << "\n";
			return LOAD_SIZE_MISMATCH;
		}
		else	// additional data is config
		{
			m_cascconf.Load(puiBuf + iSize);
		}
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

	unsigned int iSize = (unsigned int)GetTofSize();
	int iRet = LOAD_SUCCESS;

	FILE *pf = fopen(pcFileName,"rb");
	if(!pf)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not open file \"" << pcFileName << "\"."
			   << "\n";
		return LOAD_FAIL;
	}

	bool bHasConf = false;

	unsigned int uiFileSize = GetFileSize(pf);
	if(uiFileSize != iSize*sizeof(int))
	{
		if(uiFileSize < iSize*sizeof(int))
		{
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "Loader: TOF file size (" << uiFileSize << " bytes) "
				<< "!= expected size (" << iSize*sizeof(int)
				<< " bytes).\n";

			iRet = LOAD_SIZE_MISMATCH;
		}
		else	// additional data is config
		{
			bHasConf = true;
		}
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

	if(bHasConf)
	{
		m_cascconf.Load(pf, uiFileSize - iSize*sizeof(int));
	}

	fclose(pf);

	// load overlay config from optional external file
	m_cascconf.Load(pcFileName, ".conf");
	
// falls PowerPC, ints von little zu big endian konvertieren
#ifdef __BIG_ENDIAN__
	for(int i=0; i<iExpectedSize; ++i)
		m_puiDaten[i] = endian_swap(m_puiDaten[i]);
#endif
	return iRet;
}

int TofImage::SaveFile(const char *pcFileName)
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
								GetTofSize(), pf);

	int iRet = SAVE_SUCCESS;
	if(uiLen != (unsigned int)GetTofSize())
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not write file \"" << pcFileName << "\"."
			   << "\n";
		iRet = SAVE_FAIL;
	}

	fclose(pf);
	return iRet;
}

unsigned int TofImage::GetCounts() const
{
	int iXStart, iXEnd, iYStart, iYEnd;

	if(m_bUseRoi)
	{
		BoundingRect rect = m_roi.GetBoundingRect();
		iXStart = rect.bottomleft[0];
		iYStart = rect.bottomleft[1];
		iXEnd = rect.topright[0];
		iYEnd = rect.topright[1];
	}
	else
	{
		iXStart = 0;
		iYStart = 0;
		iXEnd = GetTofConfig().GetImageWidth();
		iYEnd = GetTofConfig().GetImageHeight();
	}

	TmpImage img = GetOverview();

	unsigned int uiCnt = 0;
	for(int iY=iYStart; iY<iYEnd; ++iY)
		for(int iX=iXStart; iX<iXEnd; ++iX)
		{
			if(m_bUseRoi)
			{
				if(m_roi.IsInside(iX,iY))
					uiCnt += img.GetData(iX, iY);

				//double dFractionInRoi = m_roi.HowMuchInside(iX, iY);
				//uiCnt += double(img.GetData(iX, iY)) * dFractionInRoi;
			}
			else
			{
				uiCnt += img.GetData(iX, iY);
			}
		}

	return uiCnt;
}

unsigned int TofImage::GetCountsSubtractBackground() const
{
	int iXEnd = GetTofConfig().GetImageWidth();
	int iYEnd = GetTofConfig().GetImageHeight();

	TmpImage img = GetOverview();

	unsigned int uiCnt = 0;
	unsigned int uiCntOutsideRoi = 0;

	double dTotalAreaInRoi = 0.;
	double dTotalAreaNotInRoi = 0.;

	for(int iY=0; iY<iYEnd; ++iY)
		for(int iX=0; iX<iXEnd; ++iX)
		{
			double dAreaInRoi, dAreaNotInRoi;

			if(m_roi.IsInside(iX, iY))
			{
				uiCnt += img.GetData(iX, iY);
				dAreaInRoi = 1.;
				dAreaNotInRoi = 0.;
			}
			else
			{
				uiCntOutsideRoi += img.GetData(iX, iY);
				dAreaInRoi = 0.;
				dAreaNotInRoi = 1.;
			}

			dTotalAreaInRoi += dAreaInRoi;
			dTotalAreaNotInRoi += dAreaNotInRoi;
		}

	if(float_equal<double>(dTotalAreaNotInRoi, 0.))
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "Loader: Area outside ROI is 0.\n";
	}
	else
	{
		unsigned int uiToSubtract = (unsigned int)
				(double(uiCntOutsideRoi)/dTotalAreaNotInRoi*dTotalAreaInRoi);

		if(uiToSubtract > uiCnt)
			uiCnt = 0;
		else
			uiCnt -= uiToSubtract;				
	}

	return uiCnt;
}

unsigned int TofImage::GetCounts(int iFoil) const
{
	int iXStart, iXEnd, iYStart, iYEnd;

	if(m_bUseRoi)
	{
		BoundingRect rect = m_roi.GetBoundingRect();
		iXStart = rect.bottomleft[0];
		iYStart = rect.bottomleft[1];
		iXEnd = rect.topright[0];
		iYEnd = rect.topright[1];
	}
	else
	{
		iXStart = 0;
		iYStart = 0;
		iXEnd = GetTofConfig().GetImageWidth();
		iYEnd = GetTofConfig().GetImageHeight();
	}

	TmpImage img = GetFoil(iFoil, m_bUseRoi);

	unsigned int uiCnt = 0;
	for(int iY=iYStart; iY<iYEnd; ++iY)
		for(int iX=iXStart; iX<iXEnd; ++iX)
		{
			if(m_bUseRoi)
			{
				if(m_roi.IsInside(iX,iY))
					uiCnt += img.GetData(iX, iY);

				//double dFractionInRoi = m_roi.HowMuchInside(iX, iY);
				//uiCnt += double(img.GetData(iX, iY)) * dFractionInRoi;
			}
			else
			{
				uiCnt += img.GetData(iX, iY);
			}
		}

	return uiCnt;
}

unsigned int TofImage::GetCounts(int iStartX, int iEndX,
								 int iStartY, int iEndY) const
{
	GetTofConfig().CheckTofArguments(&iStartX, &iEndX, &iStartY, &iEndY);

	TmpImage img = GetOverview();

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
	TmpImage img(&m_config);

	GetTofConfig().CheckTofArguments(&iStartX, &iEndX, &iStartY, &iEndY,
								     &iFolie, &iZ);

	int iBildBreite = abs(iEndX-iStartX);
	int iBildHoehe = abs(iEndY-iStartY);

	img.Clear();
	img.m_iW = iBildBreite;
	img.m_iH = iBildHoehe;
	img.m_puiDaten = (unsigned int*)gc.malloc(sizeof(int)*iBildHoehe*iBildBreite,
												"tof_image -> roi");

	unsigned int *puiWave = img.m_puiDaten;
	if(puiWave==NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line "
			   << __LINE__ << ")!\n";
		return img;
	}

	for(int iY=iStartY; iY<iEndY; ++iY)
		for(int iX=iStartX; iX<iEndX; ++iX)
			puiWave[(iX-iStartX) + (iY-iStartY)*iBildBreite] =
											GetData(iFolie,iZ,iX,iY);

	return img;
}


TmpGraph TofImage::GetGraph(int iStartX, int iEndX, int iStartY, int iEndY,
						    int iFoil, bool bIgnoreRoi) const
{
	const int iShiftMethod = GlobalConfig::GetShiftMethod();
	const double dNumOsc = GetTofConfig().GetNumOscillations();
	const int iNumTc = GetTofConfig().GetImagesPerFoil();
	const double dNumTc = double(iNumTc);
	const int iNumFoils = GetTofConfig().GetFoilCount();
	const int iLenX = GetTofConfig().GetImageWidth();
	const int iLenY = GetTofConfig().GetImageHeight();
	const double dLenX = double(iLenX);
	const double dLenY = double(iLenY);
	
	const TofImage *pTof = this;

	//--------------------------------------------------------------------------
	InstrumentConfig& instr = GlobalConfig::GetInstrConfig();
	
	const bool bPathLengthCorrection = instr.GetUsePathLenCorr();
	const double dDetLenX = instr.GetDetLenX();
	const double dDetLenY = instr.GetDetLenY();
	const double dMiddleX = instr.GetDetCenterX();
	const double dMiddleY = instr.GetDetCenterY();
	const double Ls = instr.GetLs();
	const double v_n = instr.GetV();
	const double dOmegaM = instr.GetOmegaM();
	//--------------------------------------------------------------------------

	bool (Fourier::*corr)(double, const double*, double *, double);
	corr = &Fourier::shift_sin;
	
	if(bPathLengthCorrection)
	{
		pTof = this->copy();

		double *pTc = new double[iNumTc];
		double *pTcShifted = new double[iNumTc];

		Fourier fourier(iNumTc);
		t_corrfkt corr = get_correction_fkt(iShiftMethod);

		// phase-correct each pixel in the region
		for(int iY=iStartY; iY<iEndY; ++iY)
			for(int iX=iStartX; iX<iEndX; ++iX)
			{
				for(int iTc=0; iTc<iNumTc; ++iTc)
					pTc[iTc] = double(pTof->GetData(iFoil, iTc, iX, iY));

				double dX = dDetLenX*(double(iX)+0.5)/dLenX - dMiddleX;
				double dY = dDetLenY*(double(iY)+0.5)/dLenY - dMiddleY;

				double dPathDiff = sqrt(dX*dX + dY*dY + Ls*Ls) - Ls;
				double dTimeDiff = dPathDiff / v_n;
				double dPhaseDiff = dOmegaM * dTimeDiff;
				dPhaseDiff = fmod(dPhaseDiff, 2.*M_PI);

				(fourier.*corr)(dNumOsc, pTc, pTcShifted, -dPhaseDiff);

				// write rebinned timechannel data
				for(int iTc=0; iTc<iNumTc; ++iTc)
					const_cast<TofImage*>(pTof)->SetData(iFoil, iTc, iX, iY,
												(unsigned int)pTcShifted[iTc]);
			}

		delete[] pTc;
		delete[] pTcShifted;
	}


	TmpGraph graph(&GetTofConfig());
	GetTofConfig().CheckTofArguments(&iStartX,&iEndX,&iStartY,&iEndY,&iFoil);

	graph.m_iW = GetTofConfig().GetImagesPerFoil();
	graph.m_puiDaten = (unsigned int*)gc.malloc(
							sizeof(int) * GetTofConfig().GetImagesPerFoil(),
							"tof_image -> graph");
	unsigned int *puiWave = graph.m_puiDaten;

	for(int iZ0=0; iZ0<GetTofConfig().GetImagesPerFoil(); ++iZ0)
	{
		unsigned int uiSummedVal=0;
		for(int iY=iStartY; iY<iEndY; ++iY)
			for(int iX=iStartX; iX<iEndX; ++iX)
			{
				if(bIgnoreRoi)
					uiSummedVal += pTof->GetData(iFoil, iZ0, iX, iY);
				else
					uiSummedVal += pTof->GetDataInsideROI(iFoil, iZ0, iX, iY);
			}

		puiWave[iZ0]=uiSummedVal;
	}

	if(bPathLengthCorrection)
	{
		delete pTof;
		pTof = 0;
	}

	return graph;
}

TmpGraph TofImage::GetGraph(int iFoil) const
{
	int iStartX = 0,
		iStartY = 0,
		iEndX = GetTofConfig().GetImageWidth(),
		iEndY = GetTofConfig().GetImageHeight();

	return GetGraph(iStartX, iEndX, iStartY, iEndY, iFoil);
}

TmpGraph TofImage::GetTotalGraph() const
{
	int iStartX = 0,
		iStartY = 0,
		iEndX = GetTofConfig().GetImageWidth(),
		iEndY = GetTofConfig().GetImageHeight();

	return GetTotalGraph(iStartX, iEndX, iStartY, iEndY);
}

TmpGraph TofImage::GetTotalGraph(int iStartX, int iEndX, int iStartY, int iEndY) const
{
	const int iShiftMethod = GlobalConfig::GetShiftMethod();
	t_corrfkt corr = get_correction_fkt(iShiftMethod);
	
	const double dNumOsc = GetTofConfig().GetNumOscillations();
	const int iNumTc = GetTofConfig().GetImagesPerFoil();
	const double dNumTc = double(iNumTc);
	const int iNumFoils = GetTofConfig().GetFoilCount();

	TmpGraph graph(&GetTofConfig());
	GetTofConfig().CheckTofArguments(&iStartX, &iEndX, &iStartY, &iEndY);

	//graph.m_TofConfig.SetNumOscillations(1.);
	graph.m_iW = iNumTc;
	graph.m_puiDaten = (unsigned int*)gc.malloc(sizeof(int) * iNumTc,
										"tof_image -> total graph");

	unsigned int *puiData = graph.m_puiDaten;
	memset(puiData, 0, sizeof(int)*iNumTc);


	// get phases for each foil
	double *pPhases = new double[iNumFoils];
	autodeleter<double> _a0(pPhases, 1);

	double dMeanPhase = 0.;
	double dTotalCounts = 0.;

	for(int iFoil=0; iFoil<iNumFoils; ++iFoil)
	{
		TmpGraph graphFoil = GetGraph(iFoil);

		double dFreq, dPhase, dAmp, dOffs;
		graphFoil.FitSinus(dFreq, dPhase, dAmp, dOffs);

		pPhases[iFoil] = dPhase;

		// count-weighted phase sum
		dMeanPhase += dPhase * double(graphFoil.Sum());
		dTotalCounts += double(graphFoil.Sum());
	}

	dMeanPhase /= dTotalCounts;
	dMeanPhase = fmod(dMeanPhase, 2.*M_PI);


	// add all foils with correct phase-shifting
	double *pDataFoil = new double[iNumTc];
	double *pDataFoilShifted = new double[iNumTc];
	double *pDataSum = new double[iNumTc];

	autodeleter<double> _a1(pDataFoil, 1);
	autodeleter<double> _a2(pDataFoilShifted, 1);
	autodeleter<double> _a3(pDataSum, 1);


	memset(pDataSum, 0, sizeof(double)*iNumTc);

	Fourier fourier(iNumTc);

	for(int iFoil=0; iFoil<GetTofConfig().GetFoilCount(); ++iFoil)
	{
		for(int iTc=0; iTc<iNumTc; ++iTc)
		{
			pDataFoil[iTc] = 0.;
			for(int iY=iStartY; iY<iEndY; ++iY)
				for(int iX=iStartX; iX<iEndX; ++iX)
					pDataFoil[iTc] += GetDataInsideROI(iFoil, iTc, iX, iY);
		}

		//std::cout << "phase foil " << iFoil << ": " << pPhases[iFoil] << std::endl;

		// shift to mean phase
		(fourier.*corr)(dNumOsc, pDataFoil, pDataFoilShifted,
						pPhases[iFoil]-dMeanPhase);

		// sum all foils
		for(int iTc=0; iTc<iNumTc; ++iTc)
			pDataSum[iTc] += pDataFoilShifted[iTc];
	}

	for(int iTc=0; iTc<iNumTc; ++iTc)
		puiData[iTc] = (unsigned int)(pDataSum[iTc]);

	return graph;
}

TmpImage TofImage::GetOverview(bool bOnlyInRoi) const
{
	TmpImage img(&m_config);

	img.Clear();
	img.m_iW = GetTofConfig().GetImageWidth();
	img.m_iH = GetTofConfig().GetImageHeight();

	img.m_puiDaten = (unsigned int*)gc.malloc(sizeof(int)*
										   GetTofConfig().GetImageWidth()*
										   GetTofConfig().GetImageHeight(),
										   "tof_image -> overview");
	if(img.m_puiDaten==NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line "
			   << __LINE__ << ")!\n";
		return img;
	}
	memset(img.m_puiDaten,0,sizeof(int)*img.m_iW*img.m_iH);

	for(int iFolie=0; iFolie<GetTofConfig().GetFoilCount(); ++iFolie)
		for(int iZ0=0; iZ0<GetTofConfig().GetImagesPerFoil(); ++iZ0)
			for(int iY=0; iY<GetTofConfig().GetImageHeight(); ++iY)
				for(int iX=0; iX<GetTofConfig().GetImageWidth(); ++iX)
				{
					if(bOnlyInRoi)
						img.m_puiDaten[iY*GetTofConfig().GetImageWidth()+iX] +=
											GetDataInsideROI(iFolie,iZ0,iX,iY);
					else
						img.m_puiDaten[iY*GetTofConfig().GetImageWidth()+iX] +=
											GetData(iFolie,iZ0,iX,iY);
				}

	return img;
}

TmpImage TofImage::GetFoil(int iFoil, bool bOnlyInRoi) const
{
	TmpImage img(&m_config);

	img.Clear();
	img.m_iW = GetTofConfig().GetImageWidth();
	img.m_iH = GetTofConfig().GetImageHeight();

	img.m_puiDaten = (unsigned int*)gc.malloc(sizeof(int)*
										   GetTofConfig().GetImageWidth()*
										   GetTofConfig().GetImageHeight(),
										   "tof_image -> foil");
	if(img.m_puiDaten==NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line "
			   << __LINE__ << ")!\n";
		return img;
	}
	memset(img.m_puiDaten,0,sizeof(int)*img.m_iW*img.m_iH);

	for(int iZ0=0; iZ0<GetTofConfig().GetImagesPerFoil(); ++iZ0)
		for(int iY=0; iY<GetTofConfig().GetImageHeight(); ++iY)
			for(int iX=0; iX<GetTofConfig().GetImageWidth(); ++iX)
			{
				if(bOnlyInRoi)
					img.m_puiDaten[iY*GetTofConfig().GetImageWidth()+iX] +=
										GetDataInsideROI(iFoil,iZ0,iX,iY);
				else
					img.m_puiDaten[iY*GetTofConfig().GetImageWidth()+iX] +=
										GetData(iFoil,iZ0,iX,iY);
			}

	return img;
}

TmpImage TofImage::GetPhaseGraph(int iFolie, bool bInDeg) const
{
	TmpImage img(&m_config);
	bool bUseFourierMethod = GlobalConfig::GetUseFFT();

	int iStartX = 0,
		iStartY = 0,
		iEndX = GetTofConfig().GetImageWidth(),
		iEndY = GetTofConfig().GetImageHeight();

	GetTofConfig().CheckTofArguments(&iStartX, &iEndX, &iStartY, &iEndY);

	img.Clear();
	img.m_iW = abs(iEndX-iStartX);
	img.m_iH = abs(iEndY-iStartY);

	const int XSIZE = GlobalConfig::iPhaseBlockSize[0],
			  YSIZE = GlobalConfig::iPhaseBlockSize[1];

	double *pdWave = (double*)gc.malloc(
							sizeof(double)*(img.m_iW+XSIZE) *(img.m_iH+YSIZE),
							"tof_image -> phase graph");
	if(pdWave==NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line "
			   << __LINE__ << ")!\n";
		return img;
	}
	img.m_pdDaten = pdWave;

	int iTc = GetTofConfig().GetImagesPerFoil();
	double dNumOsc = GetTofConfig().GetNumOscillations();

	Fourier *pFourier = 0;
	double *dIn = 0;
	if(bUseFourierMethod)
	{
		dIn = new double[iTc];
		pFourier = new Fourier(iTc);
	}

	for(int iY=iStartY; iY<iEndY; iY+=YSIZE)
		for(int iX=iStartX; iX<iEndX; iX+=XSIZE)
		{
			//std::cout << "x=" << iX << ", y=" << iY << std::endl;
			TmpGraph tmpGraph = GetGraph(iX, iX+XSIZE, iY, iY+YSIZE,
										iFolie, true);
			double dPhase = 0.;

			if(bUseFourierMethod)
			{
				if(!tmpGraph.IsLowerThan(GlobalConfig::GetMinCountsToFit()))
				{
					for(int i=0; i<iTc; ++i)
						dIn[i] = tmpGraph.GetData(i);

					double dContrast;
					pFourier->get_contrast(dNumOsc, dIn, dContrast, dPhase);

					//if(dContrast > 1.) dContrast = 0.;
					if(dContrast != dContrast) dContrast = 0.;
				}
			}
			else
			{
				double dFreq, dAmp, dOffs;
				bool bFitValid = tmpGraph.FitSinus(dFreq, dPhase, dAmp, dOffs);

				if(!bFitValid || dPhase!=dPhase)
					dPhase = 0.;
			}

			if(bInDeg) dPhase = dPhase*180./M_PI;

			for(int i=0; i<YSIZE; ++i)
				for(int j=0; j<XSIZE; ++j)
					pdWave[(iY-iStartY+i)*img.m_iW+(iX-iStartX+j)] = dPhase;
		}

	if(bUseFourierMethod)
	{
		delete[] dIn;
		delete pFourier;
	}

	return img;
}

TmpImage TofImage::GetContrastGraph(int iFoil) const
{
	TmpImage img(&m_config);
	bool bUseFourierMethod = GlobalConfig::GetUseFFT();

	int iStartX = 0,
		iStartY = 0,
		iEndX = GetTofConfig().GetImageWidth(),
		iEndY = GetTofConfig().GetImageHeight();

	GetTofConfig().CheckTofArguments(&iStartX, &iEndX, &iStartY, &iEndY);

	img.Clear();
	img.m_iW = iEndX-iStartX;
	img.m_iH = iEndY-iStartY;

	const int XSIZE = GlobalConfig::iContrastBlockSize[0],
			  YSIZE = GlobalConfig::iContrastBlockSize[1];

	img.m_pdDaten = (double*)gc.malloc(
						sizeof(double) * (img.m_iW+XSIZE) * (img.m_iH+YSIZE),
						"tof_image -> contrast graph");
	double *pdWave = img.m_pdDaten;
	if(pdWave==NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line "
			   << __LINE__ << ")!\n";
		return img;
	}

	int iTc = GetTofConfig().GetImagesPerFoil();
	double dNumOsc = GetTofConfig().GetNumOscillations();

	Fourier *pFourier = 0;
	double *dIn = 0;
	if(bUseFourierMethod)
	{
		dIn = new double[iTc];
		pFourier = new Fourier(iTc);
	}

	for(int iY=iStartY; iY<iEndY; iY+=YSIZE)
		for(int iX=iStartX; iX<iEndX; iX+=XSIZE)
		{
			TmpGraph tmpGraph = GetGraph(iX, iX+XSIZE, iY, iY+YSIZE,
										iFoil, true);
			double dContrast = 0.;
			double dPhase = 0.;

			if(bUseFourierMethod)
			{
				if(!tmpGraph.IsLowerThan(GlobalConfig::GetMinCountsToFit()))
				{
					for(int i=0; i<iTc; ++i)
						dIn[i] = tmpGraph.GetData(i);

					pFourier->get_contrast(dNumOsc, dIn, dContrast, dPhase);

					//if(dContrast > 1.) dContrast = 0.;
					if(dContrast != dContrast) dContrast = 0.;
				}
			}
			else
			{
				double dFreq, dPhase, dAmp, dOffs;
				bool bFitValid = tmpGraph.FitSinus(dFreq, dPhase, dAmp, dOffs);

				dContrast = fabs(dAmp/dOffs);
				if(!bFitValid || dContrast!=dContrast)
					dContrast = 0.;
			}

			for(int i=0; i<YSIZE; ++i)
				for(int j=0; j<XSIZE; ++j)
					pdWave[(iY-iStartY+i)*img.m_iW+(iX-iStartX+j)]=dContrast;
		}

	if(bUseFourierMethod)
	{
		delete[] dIn;
		delete pFourier;
	}

	return img;
}

TmpImage TofImage::AddFoils(const bool *pbKanaele) const
{
	TmpImage img(&m_config);

	unsigned int uiAusgabe[GetTofConfig().GetImageHeight()]
						  [GetTofConfig().GetImageWidth()];
	memset(uiAusgabe, 0, GetTofConfig().GetImageHeight()*
						 GetTofConfig().GetImageWidth()*sizeof(int));

	img.Clear();
	img.m_iW = GetTofConfig().GetImageWidth();
	img.m_iH = GetTofConfig().GetImageHeight();
	img.m_puiDaten = (unsigned int*)gc.malloc(sizeof(int)
										*GetTofConfig().GetImageWidth()
										*GetTofConfig().GetImageHeight(),
								"tof_image -> foil sum");

	unsigned int *puiWave = img.m_puiDaten;
	if(puiWave==NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line "
			   << __LINE__ << ")!\n";
		return img;
	}

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

	return img;
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

	pImg->Clear();
	pImg->m_iW = GetTofConfig().GetImageWidth();
	pImg->m_iH = GetTofConfig().GetImageHeight();
	pImg->m_puiDaten = (unsigned int*)gc.malloc(sizeof(int)
										*GetTofConfig().GetImageWidth()
										*GetTofConfig().GetImageHeight(),
										"tof_image -> foil sum");

	unsigned int *puiWave = pImg->m_puiDaten;
	if(puiWave==NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line "
			   << __LINE__ << ")!\n";
		return;
	}

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

TmpImage TofImage::AddPhases(const bool *pbFolien) const
{
	TmpImage img(&m_config);

	img.Clear();
	img.m_iW = GetTofConfig().GetImageWidth();
	img.m_iH = GetTofConfig().GetImageHeight();
	img.m_pdDaten = (double*)gc.malloc(sizeof(double)
											*GetTofConfig().GetImageWidth()
											*GetTofConfig().GetImageHeight(),
											"tof_image -> phase sum");

	double *pdWave = img.m_pdDaten;
	if(pdWave==NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line "
			   << __LINE__ << ")!\n";
		return img;
	}
	memset(pdWave, 0, sizeof(double)*img.m_iW*img.m_iH);

	for(int iFolie=0; iFolie<GetTofConfig().GetFoilCount(); ++iFolie)
	{
		if(!pbFolien[iFolie]) continue;

		TmpImage tmpimg = GetPhaseGraph(iFolie);
		img.Add(tmpimg);
	}

	for(int iY=0; iY<img.m_iH; ++iY)
		for(int iX=0; iX<img.m_iW; ++iX)
			pdWave[iY*img.m_iW + iX] = fmod(pdWave[iY*img.m_iW + iX], 360.);

	return img;
}

TmpImage TofImage::AddContrasts(const bool *pbFolien) const
{
	TmpImage img(&m_config);

	img.Clear();
	img.m_iW = GetTofConfig().GetImageWidth();
	img.m_iH = GetTofConfig().GetImageHeight();
	img.m_pdDaten = (double*)gc.malloc(sizeof(double)
											*GetTofConfig().GetImageWidth()
											*GetTofConfig().GetImageHeight(),
											"tof_image -> contrast sum");

	double *pdWave = img.m_pdDaten;
	if(pdWave==NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line "
			   << __LINE__ << ")!\n";
		return img;
	}

	memset(pdWave, 0, sizeof(double)*img.m_iW*img.m_iH);

	for(int iFolie=0; iFolie<GetTofConfig().GetFoilCount(); ++iFolie)
	{
		if(!pbFolien[iFolie]) continue;

		TmpImage tmpimg = GetContrastGraph(iFolie);
		img.Add(tmpimg);
	}

	return img;
}

void TofImage::Subtract(const TofImage& tof, double dTimes)
{
	for(int iFoil=0; iFoil<GetTofConfig().GetFoilCount(); ++iFoil)
		for(int iTc=0; iTc<GetTofConfig().GetImagesPerFoil(); ++iTc)
			for(int iY=0; iY<GetTofConfig().GetImageHeight(); ++iY)
				for(int iX=0; iX<GetTofConfig().GetImageWidth(); ++iX)
				{
					unsigned int uiCntThis = GetData(iFoil, iTc, iX, iY);
					unsigned int uiCntOther =
						(unsigned int)
						(double(tof.GetData(iFoil, iTc, iX, iY)) * dTimes);

					unsigned int uiCnt = 0;
					if(uiCntThis > uiCntOther)
						uiCnt = uiCntThis-uiCntOther;

					SetData(iFoil, iTc, iX, iY, uiCnt);
				}
}

void TofImage::GenerateRandomData()
{
	double dPhase = rand01()*2.*M_PI;
	for(int iTimeChannel=0; iTimeChannel<GetTofConfig().GetImagesPerFoil(); ++iTimeChannel)
	{
		for(int iY=0; iY<GetTofConfig().GetImageHeight(); ++iY)
			for(int iX=0; iX<GetTofConfig().GetImageWidth(); ++iX)
			{
				double dX = iX,
					   dY = iY,
					   dCenterX = 0.5 * double(GetTofConfig().GetImageWidth()),
					   dCenterY = 0.5 * double(GetTofConfig().GetImageHeight()),
					   dSpreadX = sqrt(dCenterX),
					   dSpreadY = sqrt(dCenterY);

				double dAmp = 100;

				dX += randmp1()*dX*0.1;
				dY += randmp1()*dY*0.1;
				dCenterX += randmp1()*dCenterX*0.1;
				dCenterY += randmp1()*dCenterY*0.1;
				dSpreadX += randmp1()*dSpreadX*0.1;
				dSpreadY += randmp1()*dSpreadY*0.1;

				dAmp += randmp1()*dAmp*0.1;

				double ddata = dAmp * exp(-0.5*(dX-dCenterX)*(dX-dCenterX)/(dSpreadX*dSpreadX))*
									 exp(-0.5*(dY-dCenterY)*(dY-dCenterY)/(dSpreadY*dSpreadY));

				double dNumOsc = GetTofConfig().GetNumOscillations();

				for(int iFoil=0; iFoil<GetTofConfig().GetFoilCount(); ++iFoil)
				{
					double dPhaseInc = 0.1 * double(iFoil)/double(GetTofConfig().GetFoilCount())*2.*M_PI;
					double dt = 1. + sin((dPhase+dPhaseInc) + 2.*M_PI*double(iTimeChannel)*dNumOsc / double(GetTofConfig().GetImagesPerFoil()));

					double dOffs = 10.;
					dOffs += randmp1()*dOffs*0.1;

					double dData = ddata*dt + dOffs;
					dData += randmp1()*dData*0.1;
					SetData(iFoil, iTimeChannel, iX, iY, (unsigned int)(dData));
				}
			}
	}
}

bool TofImage::SaveAsDat(const char* pcDat) const
{
	for(int iFoil=0; iFoil<GetTofConfig().GetFoilCount(); ++iFoil)
	{
		std::ostringstream ostrDat;
		ostrDat << pcDat << ".foil" << iFoil;
		
		std::ofstream ofstr(ostrDat.str().c_str());
		if(!ofstr.is_open())
			return false;

		ofstr << "# type: array_3d\n";
		ofstr << "# subtype: tobisown\n";
		ofstr << "# xlabel: x pixels\n";
		ofstr << "# ylabel: y pixels\n";
		ofstr << "# zlabel: time channels\n";
		
		for(int iY=0; iY<GetTofConfig().GetImageHeight(); ++iY)
		{
			for(int iX=0; iX<GetTofConfig().GetImageWidth(); ++iX)
			{
				for(int iTc=0; iTc<GetTofConfig().GetImagesPerFoil(); ++iTc)
				{
					ofstr << GetData(iFoil, iTc, iX, iY) << " ";
				}
				ofstr << "\n";
			}
			ofstr << "\n";
		}
	}

	return true;
}
