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
// Klassen zum Laden und Verarbeiten von Tof- & Pad-Dateien

#include "tofloader.h"

#include <fstream>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <vector>
#include <string.h>
#include <limits>
#include <iomanip>
#include "logger.h"
#include "helper.h"
#include "fit.h"
#include "gc.h"


//------------------------------------------------------------------------------
// TOF
TofImage::TofImage(const char *pcFileName,
				   bool bExternalMem, const TofConfig* conf)
		: m_puiDaten(0),
		  m_bExternalMem(bExternalMem),
		  m_bUseRoi(false)
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

TofImage::~TofImage() { Clear(); }

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
		delete[] m_puiDaten;
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
		//if(!m_roi.IsInside(iX, iY))
		//	return 0;

		double dFractionInRoi = m_roi.HowMuchInside(iX, iY);
		return double(GetData(iFoil, iTimechannel, iX, iY)) * dFractionInRoi;
	}

	return GetData(iFoil, iTimechannel, iX, iY);
}

unsigned int TofImage::GetDataInsideROI(int iImage, int iX, int iY) const
{
	if(m_bUseRoi)
	{
		// only continue if point is in ROI
		//if(!m_roi.IsInside(iX, iY))
		//	return 0;

		double dFractionInRoi = m_roi.HowMuchInside(iX, iY);
		return double(GetData(iImage, iX, iY)) * dFractionInRoi;
	}

	return GetData(iImage, iX, iY);
}

unsigned int* TofImage::GetRawData(void) const
{
	return m_puiDaten;
}

int TofImage::LoadMem(const char *strBuf, unsigned int strBufLen)
{
	const unsigned int *puiBuf = (unsigned int *)strBuf;
	unsigned int uiBufLen = strBufLen / 4;

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

	unsigned int uiFileSize = GetFileSize(pf);
	if(uiFileSize != iSize*sizeof(int))
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: TOF file size (" << uiFileSize << " bytes) "
			   << "!= expected size (" << iSize*sizeof(int)
			   << " bytes).\n";

		iRet = LOAD_SIZE_MISMATCH;
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
				//if(m_roi.IsInside(iX,iY))
				//	uiCnt += img.GetData(iX, iY);

				double dFractionInRoi = m_roi.HowMuchInside(iX, iY);
				uiCnt += double(img.GetData(iX, iY)) * dFractionInRoi;
			}
			else
			{
				uiCnt += img.GetData(iX, iY);
			}
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
				//if(m_roi.IsInside(iX,iY))
				//	uiCnt += img.GetData(iX, iY);

				double dFractionInRoi = m_roi.HowMuchInside(iX, iY);
				uiCnt += double(img.GetData(iX, iY)) * dFractionInRoi;
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
	img.m_puiDaten = (unsigned int*)gc.malloc(sizeof(int)*iBildHoehe*iBildBreite);

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
						    int iFoil) const
{
	TmpGraph graph(&GetTofConfig());

	GetTofConfig().CheckTofArguments(&iStartX,&iEndX,&iStartY,&iEndY,&iFoil);

	graph.m_iW = GetTofConfig().GetImagesPerFoil();
	graph.m_puiDaten = (unsigned int*)gc.malloc(sizeof(int)
										* GetTofConfig().GetImagesPerFoil());
	unsigned int *puiWave = graph.m_puiDaten;

	for(int iZ0=0; iZ0<GetTofConfig().GetImagesPerFoil(); ++iZ0)
	{
		unsigned int uiSummedVal=0;
		for(int iY=iStartY; iY<iEndY; ++iY)
			for(int iX=iStartX; iX<iEndX; ++iX)
				uiSummedVal += GetDataInsideROI(iFoil, iZ0, iX, iY);

		puiWave[iZ0]=uiSummedVal;
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

TmpGraph TofImage::GetTotalGraph(int iStartX, int iEndX, int iStartY, int iEndY,
								 double dPhaseShift) const
{
	TmpGraph graph(&GetTofConfig());
	GetTofConfig().CheckTofArguments(&iStartX, &iEndX, &iStartY, &iEndY);

	graph.m_iW = GetTofConfig().GetImagesPerFoil();
	graph.m_puiDaten = (unsigned int*)gc.malloc(sizeof(int)
										* GetTofConfig().GetImagesPerFoil());
	unsigned int *puiWave = graph.m_puiDaten;

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
										   GetTofConfig().GetImageHeight());
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
										   GetTofConfig().GetImageHeight());
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

	double *pdWave = (double*)gc.malloc(sizeof(double)*(img.m_iW+XSIZE)
													  *(img.m_iH+YSIZE));
	if(pdWave==NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line "
			   << __LINE__ << ")!\n";
		return img;
	}
	img.m_pdDaten = pdWave;

	for(int iY=iStartY; iY<iEndY; iY+=YSIZE)
		for(int iX=iStartX; iX<iEndX; iX+=XSIZE)
		{
			TmpGraph tmpGraph = GetGraph(iX, iX+XSIZE, iY, iY+YSIZE, iFolie);

			double dFreq, dPhase, dAmp, dOffs;
			bool bFitValid = tmpGraph.FitSinus(dFreq, dPhase, dAmp, dOffs);

			if(!bFitValid || dPhase!=dPhase)
				dPhase = 0.;

			if(bInDeg) dPhase = dPhase*180./M_PI;

			for(int i=0; i<YSIZE; ++i)
				for(int j=0; j<XSIZE; ++j)
					pdWave[(iY-iStartY+i)*img.m_iW+(iX-iStartX+j)] = dPhase;
		}

	return img;
}

TmpImage TofImage::GetContrastGraph(int iFoil) const
{
	TmpImage img(&m_config);

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

	img.m_pdDaten = (double*)gc.malloc(sizeof(double) * (img.m_iW+XSIZE)
													  * (img.m_iH+YSIZE));
	double *pdWave = img.m_pdDaten;
	if(pdWave==NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line "
			   << __LINE__ << ")!\n";
		return img;
	}

	for(int iY=iStartY; iY<iEndY; iY+=YSIZE)
		for(int iX=iStartX; iX<iEndX; iX+=XSIZE)
		{
			TmpGraph tmpGraph = GetGraph(iX, iX+XSIZE, iY, iY+YSIZE, iFoil);

			double dFreq, dPhase, dAmp, dOffs;
			bool bFitValid = tmpGraph.FitSinus(dFreq, dPhase, dAmp, dOffs);

			double dContrast = fabs(dAmp/dOffs);
			if(!bFitValid || dContrast!=dContrast)
				dContrast = 0.;

			for(int i=0; i<YSIZE; ++i)
				for(int j=0; j<XSIZE; ++j)
					pdWave[(iY-iStartY+i)*img.m_iW+(iX-iStartX+j)]=dContrast;
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
										*GetTofConfig().GetImageHeight());

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
										*GetTofConfig().GetImageHeight());

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
											*GetTofConfig().GetImageHeight());

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
											*GetTofConfig().GetImageHeight());

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






//------------------------------------------------------------------------------
// PAD
PadImage::PadImage(const char *pcFileName, bool bExternalMem,
				   const PadConfig* conf)
		: m_puiDaten(0),
		  m_iMin(0), m_iMax(0),
		  m_bExternalMem(bExternalMem),
		  m_bUseRoi(false)
{
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

	if(pad.m_puiDaten)
		memcpy(m_puiDaten, pad.m_puiDaten, sizeof(int)*GetPadSize());
	else
		memset(pad.m_puiDaten, 0, sizeof(int)*GetPadSize());
}

PadImage::~PadImage() { Clear(); }

void PadImage::Clear()
{
	if(m_puiDaten && !m_bExternalMem)
	{
		delete[] m_puiDaten;
		m_puiDaten=0;
	}
}

int PadImage::GetWidth() const { return GetPadConfig().GetImageWidth(); }
int PadImage::GetHeight() const { return GetPadConfig().GetImageHeight(); }
int PadImage::GetPadSize() const { return GetHeight()*GetWidth(); }
const PadConfig& PadImage::GetPadConfig() const { return m_config; }

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

int PadImage::LoadMem(const char *strBuf, unsigned int strBufLen)
{
	const unsigned int *puiBuf = (unsigned int *)strBuf;
	unsigned int uiBufLen = strBufLen / 4;

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

	unsigned int uiExpectedSize = GetPadConfig().GetImageHeight()*
								  GetPadConfig().GetImageWidth();

	unsigned int uiFileSize = GetFileSize(pf);
	if(uiFileSize != uiExpectedSize*sizeof(int))
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: PAD file size (" << uiFileSize << " bytes) "
			   << "!= expected size (" << uiExpectedSize*sizeof(int)
			   << " bytes).\n";

		iRet = LOAD_SIZE_MISMATCH;
	}

	unsigned int uiBufLen = fread(m_puiDaten, sizeof(int), uiExpectedSize, pf);
	if(!uiBufLen)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not read file \"" << pcFileName << "\"."
			   << "\n";
	}

	if(uiBufLen != (unsigned int)uiExpectedSize)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Buffer size (" << uiBufLen << " ints) != PAD size ("
			   << uiExpectedSize << " ints)."
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

int PadImage::LoadTextFile(const char* pcFileName)
{
	if(m_bExternalMem)
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "Loader: This PAD uses external memory"
				  " (line " << __LINE__ << ")!\n";
	}

	int iRet = LOAD_SUCCESS;

	FILE *pf = fopen(pcFileName,"rt");
	if(!pf)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not open file \"" << pcFileName << "\"."
		<< "\n";
		return LOAD_FAIL;
	}

	for(int iY=0; iY<GetPadConfig().GetImageHeight(); ++iY)
	{
		for(int iX=0; iX<GetPadConfig().GetImageWidth(); ++iX)
		{
			if(feof(pf))
			{
				logger.SetCurLogLevel(LOGLEVEL_WARN);
				logger << "Loader: Premature EOF (line " << __LINE__ << ")!\n";
				iRet = LOAD_SIZE_MISMATCH;
				break;
			}

			unsigned int uiVal = 0;
			fscanf(pf, "%d", &uiVal);

			SetData(iX, iY, uiVal);
		}

		if(iRet!=LOAD_SUCCESS)
			break;
	}

	fclose(pf);
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

unsigned int* PadImage::GetRawData(void) { return m_puiDaten; }

unsigned int PadImage::GetData(int iX, int iY) const
{
	return GetIntData(iX, iY);
}

unsigned int PadImage::GetDataInsideROI(int iX, int iY) const
{
	if(m_bUseRoi)
	{
		// only continue if point is in ROI
		//if(!m_roi.IsInside(iX, iY))
		//	return 0;

		double dFractionInRoi = m_roi.HowMuchInside(iX, iY);
		return GetDoubleData(iX, iY) * dFractionInRoi;
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

void PadImage::SetData(int iX, int iY, unsigned int uiCnt)
{
	if(m_puiDaten && iX>=0 && iX<GetPadConfig().GetImageWidth() &&
					 iY>=0 && iY<GetPadConfig().GetImageHeight())
	{
		m_puiDaten[iY*GetPadConfig().GetImageWidth() + iX] = uiCnt;
	}
}

unsigned int PadImage::GetCounts() const
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
		iXEnd = GetPadConfig().GetImageWidth();
		iYEnd = GetPadConfig().GetImageHeight();
	}

	unsigned int uiCnt = 0;

	for(int iY=iYStart; iY<iYEnd; ++iY)
		for(int iX=iXStart; iX<iXEnd; ++iX)
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


TmpImage PadImage::GetRoiImage() const
{
	TmpImage img;

	img.m_iW = GetWidth();
	img.m_iH = GetHeight();
	img.m_puiDaten = (unsigned int*)gc.malloc(sizeof(int)*img.m_iW*img.m_iH);

	for(int iY=0; iY<img.m_iH; ++iY)
		for(int iX=0; iX<img.m_iW; ++iX)
			img.m_puiDaten[iY*img.m_iW + iX] = GetDataInsideROI(iX,iY);

	return img;
}


//------------------------------------------------------------------------------
// random data generation

void PadImage::GenerateRandomData()
{
		for(int iY=0; iY<GetPadConfig().GetImageHeight(); ++iY)
			for(int iX=0; iX<GetPadConfig().GetImageWidth(); ++iX)
			{
				double dX = iX,
					   dY = iY,
					   dCenterX = 0.5 * double(GetPadConfig().GetImageWidth()),
					   dCenterY = 0.5 * double(GetPadConfig().GetImageHeight()),
					   dSpreadX = sqrt(dCenterX),
					   dSpreadY = sqrt(dCenterY),
					   dAmp = 10000.,
					   dOffs = 10.;

				dX += randmp1()*dX*0.1;
				dY += randmp1()*dY*0.1;
				dCenterX += randmp1()*dCenterX*0.1;
				dCenterY += randmp1()*dCenterY*0.1;
				dSpreadX += randmp1()*dSpreadX*0.1;
				dSpreadY += randmp1()*dSpreadY*0.1;
				dAmp += randmp1()*dAmp*0.1;
				dOffs += randmp1()*dOffs*0.1;

				double ddata = dAmp * exp(-0.5*(dX-dCenterX)*(dX-dCenterX)/(dSpreadX*dSpreadX))*
									 exp(-0.5*(dY-dCenterY)*(dY-dCenterY)/(dSpreadY*dSpreadY));

				SetData(iX, iY, (unsigned int)(ddata + dOffs));
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


//------------------------------------------------------------------------------
// TmpImage
TmpImage::TmpImage(const TofConfig* pTofConf) :
						m_iW(GlobalConfig::GetTofConfig().GetImageWidth()),
						m_iH(GlobalConfig::GetTofConfig().GetImageHeight()),
						m_puiDaten(NULL), m_pdDaten(NULL),
						m_dMin(0), m_dMax(0)
{
	if(pTofConf)
		m_TofConfig = *pTofConf;
	else
		m_TofConfig = GlobalConfig::GetTofConfig();
}

TmpImage::TmpImage(const TmpImage& tmp)
{
	operator=(tmp);
}

TmpImage& TmpImage::operator=(const TmpImage& tmp)
{
	m_iW = tmp.m_iW;
	m_iH = tmp.m_iH;
	m_dMin = tmp.m_dMin;
	m_dMax = tmp.m_dMax;
	m_puiDaten = tmp.m_puiDaten;
	m_pdDaten = tmp.m_pdDaten;
	m_TofConfig = tmp.m_TofConfig;

	gc.acquire(m_puiDaten);
	gc.acquire(m_pdDaten);

	return *this;
}

void TmpImage::Clear(void)
{
	gc.release(m_puiDaten);
	m_puiDaten=NULL;

	gc.release(m_pdDaten);
	m_pdDaten=NULL;
}

TmpImage::~TmpImage() { Clear(); }

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
				unsigned int uiVal = m_puiDaten[m_iW*iY+iX];

				if(m_dMax < uiVal)
				{
					m_vecMax[0] = iX;
					m_vecMax[1] = iY;
				}

				m_dMin = min(m_dMin, double(uiVal));
				m_dMax = max(m_dMax, double(uiVal));
			}
			else if(m_pdDaten)
			{
				double dVal = m_pdDaten[m_iW*iY+iX];

				if(m_dMax < dVal)
				{
					m_vecMax[0] = iX;
					m_vecMax[1] = iY;
				}

				m_dMin = min(m_dMin, dVal);
				m_dMax = max(m_dMax, dVal);
			}
		}
	}
}

int TmpImage::GetIntMin(void) const { return int(GetDoubleMin()); }
int TmpImage::GetIntMax(void) const { return int(GetDoubleMax()); }
double TmpImage::GetDoubleMin(void) const { return m_dMin; }
double TmpImage::GetDoubleMax(void) const { return m_dMax; }

bool TmpImage::WriteXML(const char* pcFileName,
						int iSampleDetector, double dWavelength,
						double dLifetime, int iBeamMonitor) const
{
	std::ofstream ofstr(pcFileName);
	if(!ofstr.is_open())
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not open file \""
			   << pcFileName << "\" for writing.\n";
		return false;
	}

	ofstr << "<measurement_file>\n\n";
	ofstr << "<instrument_name>MIRA</instrument_name>\n";
	ofstr << "<location>Forschungsreaktor Muenchen II - FRM2</location>\n";

	const int iRes = 1024;

	ofstr << "\n<measurement_data>\n";

	ofstr << "<Sample_Detector>" << iSampleDetector << "</Sample_Detector>\n";
	ofstr << "<wavelength>" << std::setprecision(2) << dWavelength << "</wavelength>\n";
	ofstr << "<lifetime>" << std::setprecision(3) << dLifetime << "</lifetime>\n";
	ofstr << "<beam_monitor>" << iBeamMonitor << "</beam_monitor>\n";
	ofstr << "<resolution>" << iRes << "</resolution>\n";

	ofstr << "\n<detector_value>\n";

	if(iRes % m_iW || iRes % m_iH)
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "Loader: Resolution does not match.\n";
	}

	for(int iX=0; iX<m_iW; ++iX)
	{
		for(int t1=0; t1 < iRes/m_iW; ++t1)
		{
			for(int iY=0; iY<m_iH; ++iY)
			{
				for(int t2=0; t2 < iRes/m_iH; ++t2)
				{
					if(t1%4==0 && t2%4==0)
						ofstr << GetDoubleData(iX,iY) / 4. << " ";
					else
						ofstr << "0 ";
				}
			}
			ofstr << "\n";
		}
	}

	ofstr << "</detector_value>\n\n";
	ofstr << "</measurement_data>\n";

	ofstr << "\n</measurement_file>\n";
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

	m_puiDaten = (unsigned int*)gc.malloc(sizeof(int)*m_iW*m_iH);
	if(m_puiDaten==NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line "
			   << __LINE__ << ")!\n";
		return;
	}
	memcpy(m_puiDaten, pPad->m_puiDaten, m_iW*m_iH*sizeof(int));

	UpdateRange();
}

const Vec2d<int>& TmpImage::GetMaxCoord() const { return m_vecMax; }

bool TmpImage::FitGaussian(double &dAmp,
						   double &dCenterX, double &dCenterY,
						   double &dSpreadX, double &dSpreadY) const
{
	dAmp = GetDoubleMax();
	dCenterX = double(GetMaxCoord()[0]);
	dCenterY = double(GetMaxCoord()[1]);
	dSpreadX = 1.;
	dSpreadY = 1.;

	if(m_puiDaten)
		return ::FitGaussian(m_iW, m_iH, m_puiDaten,
							 dAmp, dCenterX, dCenterY, dSpreadX, dSpreadY);
	//else if(m_pdDaten)
	// ...

	return false;
}

// TODO: do a better version of this method!
TmpGraph TmpImage::GetRadialIntegration(double dAngleInc, double dRadInc,
										const Vec2d<double>& vecCenter,
										bool bAngMean) const
{
	const double dMaxRad = sqrt((double(GetWidth())/2.)*(double(GetWidth())/2.)
						   + (double(GetHeight())/2.)*(double(GetHeight())/2.));
	const int iSteps = int(dMaxRad / dRadInc);

	TmpGraph graph(&m_TofConfig);
	graph.m_iW = iSteps;
	graph.m_puiDaten = (unsigned int*)gc.malloc(sizeof(int)*iSteps);
	memset(graph.m_puiDaten, 0, iSteps*sizeof(int));

	unsigned int uiTotalCnts = 0;

	for(int i=0; i<iSteps; ++i)
	{
		const double dBeginRad = double(i)*dRadInc;
		const double dEndRad = double(i+1)*dRadInc;

		Roi roi;
		roi.add(new RoiCircleRing(vecCenter,dBeginRad,dEndRad));

		// brute force search
		for(int iY=0; iY<GetHeight(); ++iY)
			for(int iX=0; iX<GetWidth(); ++iX)
			{
				bool bPixelInside = roi.IsInside(iX,iY) || roi.IsInside(iX,iY+1)
							|| roi.IsInside(iX+1,iY) || roi.IsInside(iX+1,iY+1);

				if(!bPixelInside)
					continue;

				double dFraction = roi.HowMuchInside(iX, iY);
				graph.m_puiDaten[i] += dFraction*double(GetIntData(iX, iY));
			}

		// bAngMean: graph is a radial slice with mean angular counts
		if(bAngMean)
		{
			graph.m_puiDaten[i] /= (dEndRad*dEndRad - dBeginRad*dBeginRad)*M_PI;
		}
		uiTotalCnts += graph.m_puiDaten[i];
	}

	if(!bAngMean)
	{
		logger.SetCurLogLevel(LOGLEVEL_INFO);
		logger << "Loader: Total counts summed = " << uiTotalCnts << "\n";
	}
	return graph;
}





//------------------------------------------------------------------------------
// TmpGraph

TmpGraph::TmpGraph(const TofConfig* pTofConf) :
			m_iW(0), m_puiDaten(0)
{
	if(pTofConf)
		m_TofConfig = *pTofConf;
	else
		m_TofConfig = GlobalConfig::GetTofConfig();
}

TmpGraph::~TmpGraph()
{
	if(m_puiDaten)
	{
		gc.release(m_puiDaten);
		m_puiDaten=NULL;
	}
}

TmpGraph::TmpGraph(const TmpGraph& tmp)
{
	operator=(const_cast<TmpGraph&>(tmp));
}

TmpGraph& TmpGraph::operator=(const TmpGraph& tmp)
{
	m_iW = tmp.m_iW;
	m_puiDaten = tmp.m_puiDaten;
	m_TofConfig = tmp.m_TofConfig;
	gc.acquire(m_puiDaten);

	return *this;
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

bool TmpGraph::FitSinus(double& dFreq, double &dPhase, double &dAmp, double &dOffs,
						double &dPhase_err, double &dAmp_err, double &dOffs_err) const
{
	if(m_iW<=0) return false;
	double dNumOsc = m_TofConfig.GetNumOscillations();

	// Freq fix
	dFreq = dNumOsc * 2.*M_PI/double(m_iW);

	if(IsLowerThan(1))
		return false;

	return ::FitSinus(m_iW, m_puiDaten, dFreq,
					  dPhase, dAmp, dOffs,
					  dPhase_err, dAmp_err, dOffs_err);
}

bool TmpGraph::FitSinus(double& dFreq, double &dPhase, double &dAmp, double &dOffs) const
{
	double dPhase_err, dAmp_err, dOffs_err;

	return FitSinus(dFreq, dPhase, dAmp, dOffs,
					dPhase_err, dAmp_err, dOffs_err);
}

bool TmpGraph::GetContrast(double &dContrast, double &dPhase,
							double &dContrast_err, double &dPhase_err) const
{
	double dFreq;
	double dAmp, dOffs;
	double dAmp_err, dOffs_err;

	if(!FitSinus(dFreq, dPhase, dAmp, dOffs, dPhase_err, dAmp_err, dOffs_err))
		return false;

	dContrast = dAmp / dOffs;
	dContrast_err = sqrt((1/dOffs*dAmp_err)*(1/dOffs*dAmp_err)
					+ (-dAmp/(dOffs*dOffs)*dOffs_err)*(-dAmp/(dOffs*dOffs)*dOffs_err));

	return true;
}

bool TmpGraph::GetContrast(double &dContrast, double &dPhase) const
{
	double dContrast_err, dPhase_err;
	return GetContrast(dContrast, dPhase, dContrast_err, dPhase_err);
}
