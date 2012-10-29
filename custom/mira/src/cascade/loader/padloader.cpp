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
// Klassen zum Laden und Verarbeiten von Pad-Dateien

#include "padloader.h"

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
#include "../aux/gc.h"


PadImage::PadImage(const char *pcFileName, bool bExternalMem,
				   const PadConfig* conf)
		: m_puiDaten(0),
		  m_iMin(0), m_iMax(0),
		  m_bExternalMem(bExternalMem),
		  m_bUseRoi(false),
		  m_bOk(false)
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
		m_puiDaten = (unsigned int*)gc.malloc(sizeof(int)*GetPadSize(),
												"pad_image");
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

	m_bOk = pad.IsOk();

	m_puiDaten = (unsigned int*)gc.malloc(sizeof(int)*GetPadSize(), "pad_image");
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

bool PadImage::IsOk() const { return m_bOk; }

PadImage::~PadImage() { Clear(); }

void PadImage::Clear()
{
	if(m_puiDaten && !m_bExternalMem)
	{
		gc.release(m_puiDaten);
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
		if(uiBufLen < (unsigned int)GetPadConfig().GetImageHeight()*
			GetPadConfig().GetImageWidth())
		{
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "Loader: Buffer size (" << uiBufLen << " ints) != PAD size ("
				<< GetPadConfig().GetImageHeight()*
					GetPadConfig().GetImageWidth()
				<< " ints)." << "\n";
			return LOAD_SIZE_MISMATCH;
		}
		else	// additional data is config
		{
			m_cascconf.Load(puiBuf + GetPadConfig().GetImageHeight()*
										GetPadConfig().GetImageWidth());
		}
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

	bool bHasConf = false;

	unsigned int uiExpectedSize = GetPadConfig().GetImageHeight()*
								  GetPadConfig().GetImageWidth();

	unsigned int uiFileSize = GetFileSize(pf);
	if(uiFileSize != uiExpectedSize*sizeof(int))
	{
		if(uiFileSize < uiExpectedSize*sizeof(int))
		{
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "Loader: PAD file size (" << uiFileSize << " bytes) "
				<< "!= expected size (" << uiExpectedSize*sizeof(int)
				<< " bytes).\n";

			iRet = LOAD_SIZE_MISMATCH;
		}
		else	// additional data is config
		{
			bHasConf = true;
		}
		
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

	if(bHasConf)
	{
		m_cascconf.Load(pf, uiFileSize - GetPadConfig().GetImageHeight()*
							GetPadConfig().GetImageWidth()*sizeof(int));
	}
	
	fclose(pf);

	// load overlay config from optional external file
	m_cascconf.Load(pcFileName, ".conf");


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

unsigned int PadImage::GetDataInsideROI(int iX, int iY,
										double *dArea) const
{
	if(m_bUseRoi)
	{
		// only continue if point is in ROI
		//if(!m_roi.IsInside(iX, iY))
		//	return 0;

		double dFractionInRoi = m_roi.HowMuchInside(iX, iY);
		if(dArea)
			*dArea = dFractionInRoi;

		return GetDoubleData(iX, iY) * dFractionInRoi;
	}
	return GetData(iX, iY);
}

unsigned int PadImage::GetDataOutsideROI(int iX, int iY,
										double *dArea) const
{
	if(m_bUseRoi)
	{
		// only continue if point is not in ROI
		//if(m_roi.IsInside(iX, iY))
		//	return 0;

		double dFractionNotInRoi = 1.-m_roi.HowMuchInside(iX, iY);
		if(dArea)
			*dArea = dFractionNotInRoi;

		return GetDoubleData(iX, iY) * dFractionNotInRoi;
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

unsigned int PadImage::GetCountsSubtractBackground() const
{
	int iXEnd = GetPadConfig().GetImageWidth();
	int iYEnd = GetPadConfig().GetImageHeight();

	unsigned int uiCnt = 0;
	unsigned int uiCntOutsideRoi = 0;

	double dTotalAreaInRoi = 0.;
	double dTotalAreaNotInRoi = 0.;

	for(int iY=0; iY<iYEnd; ++iY)
		for(int iX=0; iX<iXEnd; ++iX)
		{
			double dAreaInRoi, dAreaNotInRoi;

			uiCnt += GetDataInsideROI(iX, iY, &dAreaInRoi);
			uiCntOutsideRoi += GetDataOutsideROI(iX, iY, &dAreaNotInRoi);

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
	img.m_puiDaten = (unsigned int*)gc.malloc(sizeof(int)*img.m_iW*img.m_iH,
										"pad_image -> roi");

	for(int iY=0; iY<img.m_iH; ++iY)
		for(int iX=0; iX<img.m_iW; ++iX)
			img.m_puiDaten[iY*img.m_iW + iX] = GetDataInsideROI(iX,iY);

	return img;
}

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

bool PadImage::SaveAsDat(const char* pcDat) const
{
	std::ofstream ofstr(pcDat);
	if(!ofstr.is_open())
		return false;

	ofstr << "# type: array_2d\n";
	ofstr << "# subtype: tobisown\n";
	ofstr << "# xlabel: x pixels\n";
	ofstr << "# ylabel: y pixels\n";
	ofstr << "# zlabel: counts\n";

	for(int iY=0; iY<GetPadConfig().GetImageHeight(); ++iY)
	{
		for(int iX=0; iX<GetPadConfig().GetImageWidth(); ++iX)
			ofstr << GetData(iX, iY) << " ";
		ofstr << "\n";
	}

	ofstr.close();
	return true;
}
