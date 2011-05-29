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

// Klassen zum Laden und Verarbeiten von Tof- & Pad-Dateien

#include "tofloader.h"
#include "config.h"

#include <fstream>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <vector>
#include <string.h>
#include <limits>
#include <iostream>
#include "logger.h"
#include "helper.h"

#ifdef USE_MINUIT
	#include <Minuit2/FCNBase.h>
	#include <Minuit2/FunctionMinimum.h>
	#include <Minuit2/MnMigrad.h>
	#include <Minuit2/MnUserParameters.h>
	#include <Minuit2/MnPrint.h>
#endif

//////////////////////////// Konfiguration ///////////////////////////
// Default-Werte
int Config_TofLoader::FOIL_COUNT = 6;
int Config_TofLoader::IMAGES_PER_FOIL = 8;		// Zeitkanäle
int Config_TofLoader::IMAGE_WIDTH = 128;
int Config_TofLoader::IMAGE_HEIGHT = 128;
int Config_TofLoader::IMAGE_COUNT = 192;
int *Config_TofLoader::piFoilBegin = 0 /*{0, 32, 128, 160}*/;

int Config_TofLoader::iPhaseBlockSize[2] = {1, 2};
int Config_TofLoader::iContrastBlockSize[2] = {1, 2};

double Config_TofLoader::LOG_LOWER_RANGE = -0.5;
bool Config_TofLoader::USE_PSEUDO_COMPRESSION = 1;


void Config_TofLoader::Init()
{
#ifdef __BIG_ENDIAN__
	logger.SetCurLogLevel(LOGLEVEL_INFO);
	logger << "Loader: This is a PowerPC (big endian).\n";
#endif
	
#ifndef USE_MINUIT
	logger.SetCurLogLevel(LOGLEVEL_ERR);
	logger << "Loader: Minuit not available." << "\n";
#endif
	
	Deinit();

// Cascade-Qt-Client lädt Einstellungen über XML-Datei
#ifdef __CASCADE_QT_CLIENT__	
	IMAGE_COUNT = Config::GetSingleton()->QueryInt("/cascade_config/tof_file/image_count", IMAGE_COUNT);
	FOIL_COUNT = Config::GetSingleton()->QueryInt("/cascade_config/tof_file/foil_count", FOIL_COUNT);
	IMAGES_PER_FOIL = Config::GetSingleton()->QueryInt("/cascade_config/tof_file/images_per_foil", IMAGES_PER_FOIL);
	IMAGE_WIDTH = Config::GetSingleton()->QueryInt("/cascade_config/tof_file/image_width", IMAGE_WIDTH);
	IMAGE_HEIGHT = Config::GetSingleton()->QueryInt("/cascade_config/tof_file/image_height", IMAGE_HEIGHT);
	USE_PSEUDO_COMPRESSION = Config::GetSingleton()->QueryInt("/cascade_config/tof_file/pseudo_compression", USE_PSEUDO_COMPRESSION);
	
	piFoilBegin = new int[FOIL_COUNT];
	for(int i=0; i<FOIL_COUNT; ++i)
	{
		char pcStr[256];
		sprintf(pcStr, "/cascade_config/tof_file/foil_%d_start", i+1);
		piFoilBegin[i] = Config::GetSingleton()->QueryInt(pcStr, IMAGES_PER_FOIL*2*i /*default*/ );
	}
	
	iPhaseBlockSize[0] = Config::GetSingleton()->QueryInt("/cascade_config/graphs/phase_block_size_x", iPhaseBlockSize[0]);
	iPhaseBlockSize[1] = Config::GetSingleton()->QueryInt("/cascade_config/graphs/phase_block_size_y", iPhaseBlockSize[1]);
	iContrastBlockSize[0] = Config::GetSingleton()->QueryInt("/cascade_config/graphs/contrast_block_size_x", iContrastBlockSize[0]);
	iContrastBlockSize[1] = Config::GetSingleton()->QueryInt("/cascade_config/graphs/contrast_block_size_y", iContrastBlockSize[1]);
	
	LOG_LOWER_RANGE = Config::GetSingleton()->QueryDouble("/cascade_config/graphs/log_lower_range", LOG_LOWER_RANGE);
	
#else	// Nicos-Client holt Einstellungen von Detektor

	// Defaults setzen
	piFoilBegin = new int[FOIL_COUNT];
	for(int i=0; i<FOIL_COUNT; ++i)
		piFoilBegin[i] = IMAGES_PER_FOIL*2*i /*default*/;
	
	// TODO: richtige Einstellungen holen oder mit den Setter-Funktionen setzen
#endif
}

void Config_TofLoader::Deinit()
{
	if(piFoilBegin)
	{
		delete[] piFoilBegin;
		piFoilBegin = 0;
	}
}

///////////////////////////////////////// Getter & Setter ////////////////////////////////
double Config_TofLoader::GetLogLowerRange() { return LOG_LOWER_RANGE; }
int Config_TofLoader::GetFoilCount() { return FOIL_COUNT; }
int Config_TofLoader::GetImagesPerFoil() { return IMAGES_PER_FOIL; }
int Config_TofLoader::GetImageWidth() { return IMAGE_WIDTH; }
int Config_TofLoader::GetImageHeight() { return IMAGE_HEIGHT; }
int Config_TofLoader::GetImageCount() { return IMAGE_COUNT; }
bool Config_TofLoader::GetPseudoCompression() { return USE_PSEUDO_COMPRESSION; }

int Config_TofLoader::GetFoilBegin(int iFoil)
{
	if(iFoil<0 || iFoil>=FOIL_COUNT) return -1;
	return piFoilBegin[iFoil];
}

static inline int GetNextPowerOfTwo(int iNum)
{
	int i=0;
	while(1)
	{
		if(iNum < (1<<i)) break;
		++i;
	}
	return 1<<i;
}

void Config_TofLoader::SetFoilCount(int iNumFoils)
{
	Deinit();
	FOIL_COUNT = iNumFoils;
	piFoilBegin = new int[iNumFoils];
	
	for(int i=0; i<iNumFoils; ++i)					// halbvernünftige Default-Werte setzen
		piFoilBegin[i] = GetNextPowerOfTwo(IMAGES_PER_FOIL)*i;	//
}

void Config_TofLoader::SetImagesPerFoil(int iNumImagesPerFoil) { IMAGES_PER_FOIL = iNumImagesPerFoil; }
void Config_TofLoader::SetImageWidth(int iImgWidth) { IMAGE_WIDTH = iImgWidth; }
void Config_TofLoader::SetImageHeight(int iImgHeight) { IMAGE_HEIGHT = iImgHeight; }
void Config_TofLoader::SetImageCount(int iImgCount) { IMAGE_COUNT = iImgCount; }
void Config_TofLoader::SetPseudoCompression(bool bSet) { USE_PSEUDO_COMPRESSION = bSet; }

void Config_TofLoader::SetFoilBegin(int iFoil, int iOffs)
{
	if(iFoil<0 || iFoil>=FOIL_COUNT) return;
	
	piFoilBegin[iFoil] = iOffs;
}
//////////////////////////////////////////////////////////////////////////////////////////

void Config_TofLoader::CheckArguments(int* piStartX, int* piEndX, int* piStartY, int* piEndY, int* piFolie, int* piZ)
{	
	if(piStartX && piEndX && piStartY && piEndY)
	{
		if(*piStartX>*piEndX) { int iTmp = *piStartX; *piStartX = *piEndX; *piEndX = iTmp; }
		if(*piStartY>*piEndY) { int iTmp = *piStartY; *piStartY = *piEndY; *piEndY = iTmp; }
		
		if(*piStartX<0) 
			*piStartX = 0;
		else if(*piStartX>Config_TofLoader::Config_TofLoader::GetImageWidth()) 
			*piStartX = Config_TofLoader::Config_TofLoader::GetImageWidth();
		if(*piEndX<0) 
			*piEndX = 0;
		else if(*piEndX>Config_TofLoader::Config_TofLoader::GetImageWidth()) 
			*piEndX = Config_TofLoader::Config_TofLoader::GetImageWidth();
		
		if(*piStartY<0) 
			*piStartY = 0;
		else if(*piStartY>Config_TofLoader::Config_TofLoader::GetImageHeight()) 
			*piStartY = Config_TofLoader::Config_TofLoader::GetImageHeight();
		if(*piEndY<0) 
			*piEndY = 0;
		else if(*piEndY>Config_TofLoader::Config_TofLoader::GetImageHeight()) 
			*piEndY = Config_TofLoader::Config_TofLoader::GetImageHeight();
	}
	
	if(piFolie)
	{
		if(*piFolie<0)
			*piFolie=0;
		if(*piFolie>=Config_TofLoader::FOIL_COUNT)
			*piFolie = Config_TofLoader::FOIL_COUNT-1;
	
	}
	if(piZ)
	{
		if(*piZ<0)
			*piZ = 0;
		if(*piZ>=Config_TofLoader::IMAGES_PER_FOIL)
			*piZ=Config_TofLoader::IMAGES_PER_FOIL-1;
	}
}

bool Config_TofLoader::GuessConfigFromSize(bool bPseudoCompressed, int iLen, bool bIsTof, bool bFirstCall)
{
	if(bFirstCall)
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "Loader: Trying to guess correct configuration. (Please configure the loader correctly using either Config_TofLoader or the config file.)\n";
	}

	static const int MIN_SHIFT = 6;		// 64
 	static const int MAX_SHIFT = 10;	// 1024
	static const int MIN_LEN = 1<<MIN_SHIFT;
	static const int MAX_LEN = 1<<MAX_SHIFT;	
	
	const int iKnownX[] = 	{64,  128};
	const int iKnownY[] = 	{128, 128};
	const int iKnownCnt[] = {196, 128};
	
	if(bIsTof && !bPseudoCompressed)	// TOF
	{
		bool bFound=false;
	
		// bekannte Konfigurationen absuchen
		for(int i=0; i<sizeof(iKnownCnt)/sizeof(int); ++i)
		{
			if(iKnownX[i]*iKnownY[i]*iKnownCnt[i] != iLen) continue;
			GuessConfigFromSize(bPseudoCompressed,iKnownX[i]*iKnownY[i],false,false);
			
			bFound = true;
			IMAGE_WIDTH = iKnownX[i];
			IMAGE_HEIGHT = iKnownY[i];
			IMAGE_COUNT = iKnownCnt[i];
		}		
		
		if(!bFound)
		{
			// 2er-Potenzen absuchen
			for(int i=MIN_SHIFT; i<MAX_SHIFT; ++i)
			{
				int iImgCnt = 1<<i;
				if(iLen % iImgCnt) continue;
				
				if(GuessConfigFromSize(bPseudoCompressed,iLen/iImgCnt, false, false))
				{
					bFound = true;
					IMAGE_COUNT = iImgCnt;
					break;
				}
			}
		}
		
		if(!bFound)
		{
			// alles absuchen
			for(int i=MIN_LEN; i<MAX_LEN; ++i)
			{
				int iImgCnt = i;
				if(iLen % iImgCnt) continue;
				
				if(GuessConfigFromSize(bPseudoCompressed,iLen/iImgCnt, false, false))
				{
					bFound = true;
					IMAGE_COUNT = iImgCnt;
					break;
				}
			}			
		}
		
		if(bFound)
		{
			logger.SetCurLogLevel(LOGLEVEL_WARN);
			logger << "Loader: Guessing image count: " << IMAGE_COUNT << "\n";
		}
		return bFound;
	}
	else if(bIsTof && bPseudoCompressed)
	{
		// TODO
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Pseudo-compressed size guess not yet implemented.\n";
		return 0;
	}
	else	// PAD
	{
		bool bFound=false;
		
		// bekannte Konfigurationen absuchen
		for(int i=0; i<sizeof(iKnownCnt)/sizeof(int); ++i)
		{
			int iPadLen = iKnownX[i]*iKnownY[i];
			if(iPadLen != iLen) continue;
			
			bFound = true;
			IMAGE_WIDTH = iKnownX[i];
			IMAGE_HEIGHT = iKnownY[i];
		}		

		if(!bFound)
		{
			// 2er-Potenzen absuchen
			for(int i=MIN_SHIFT; i<MAX_SHIFT; ++i)
			{
				int iSideLenX = 1<<i;
				int iSideLenY = 0;
				for(int j=MIN_SHIFT; j<MAX_SHIFT; ++j)
				{
					iSideLenY = 1<<j;
					if(iSideLenX*iSideLenY==iLen) 
					{
						bFound=true;
						IMAGE_WIDTH = iSideLenX;
						IMAGE_HEIGHT = iSideLenY;
						break;
					}
					
					if(iSideLenX*iSideLenY > iLen)
						break;
				}
				
				if(bFound)
					break;
			}
		}

		if(!bFound)
		{
			// alles absuchen
			for(int i=MIN_LEN; i<MAX_LEN; ++i)
			{
				int j=0;
				for(j=MIN_LEN; j<MAX_LEN; ++j)
				{
					if(i*j==iLen) 
					{
						bFound=true;
						IMAGE_WIDTH = i;
						IMAGE_HEIGHT = j;
						break;
					}
					
					if(i*j > iLen) break;
				}
				
				if(bFound)
					break;
			}
		}
		
		if(bFound)
		{
			logger.SetCurLogLevel(LOGLEVEL_WARN);
			logger << "Loader: Guessing image width: " << IMAGE_WIDTH << "\n";
			logger << "Loader: Guessing image height: " << IMAGE_HEIGHT << "\n";
		}
		
		return bFound;
	}
}

void Config_TofLoader::SetLogLevel(int iLevel)
{
	logger.SetLogLevel(iLevel);
}
//////////////////////////////////////////////////////////////////////


////////////////// TOF ////////////////// 
TofImage::TofImage(const char *pcFileName, int iCompressed, bool bExternalMem) : m_bExternalMem(bExternalMem)
{
	SetCompressionMethod(iCompressed);
	m_puiDaten = 0;
	
	if(!m_bExternalMem)
	{
		int iSize = GetTofSize();
		m_puiDaten = new unsigned int[iSize];
		if(m_puiDaten==NULL)
		{
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "Loader: Could not allocate memory (line " << __LINE__ << ")!\n";
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

void TofImage::SetExternalMem(void* pvDaten) 
{ 
	if(!m_bExternalMem) return;
	
	m_puiDaten = (unsigned int*)pvDaten;
	//UpdateRange();
}

int TofImage::GetTofSize() const
{
	int iSize = m_bPseudoCompressed 
			? Config_TofLoader::GetFoilCount()*Config_TofLoader::GetImagesPerFoil()*Config_TofLoader::GetImageHeight()*Config_TofLoader::GetImageWidth()
			: Config_TofLoader::GetImageCount()*Config_TofLoader::GetImageHeight()*Config_TofLoader::GetImageWidth();		
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
			m_bPseudoCompressed=Config_TofLoader::GetPseudoCompression(); 
			break;
		default: 
			m_bPseudoCompressed=1; 
			break;
	}
}

unsigned int TofImage::GetData(int iBild, int iX, int iY) const
{
	if(m_puiDaten && iBild>=0 && iBild<Config_TofLoader::IMAGE_COUNT && iX>=0 && iX<Config_TofLoader::GetImageWidth() && iY>=0 && iY<Config_TofLoader::GetImageHeight())
		return m_puiDaten[iBild*Config_TofLoader::GetImageWidth()*Config_TofLoader::GetImageHeight() + iY*Config_TofLoader::GetImageWidth() + iX];
	return 0;
}

unsigned int TofImage::GetData(int iFoil, int iTimechannel, int iX, int iY) const
{
	if(!m_bPseudoCompressed)
	{
		int iZ = Config_TofLoader::piFoilBegin[iFoil] + iTimechannel;
		
		if(iTimechannel!=0)
			return GetData(iZ,iX,iY);
		else
			return GetData(iZ,iX,iY)+GetData(iZ+Config_TofLoader::IMAGES_PER_FOIL,iX,iY);
	}
	else
	{
		return GetData(iFoil*Config_TofLoader::IMAGES_PER_FOIL+iTimechannel, iX, iY);
	}
}

unsigned int* TofImage::GetRawData(void) const
{
	return m_puiDaten;
}

int TofImage::LoadMem(const unsigned int *puiBuf, unsigned int uiBufLen)
{
	int iSize = GetTofSize();
	
	if(uiBufLen!=(unsigned int)iSize)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Buffer size (" << uiBufLen << " ints) != TOF size (" << iSize << " ints)." << "\n";
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
	int iSize = GetTofSize();
	
	int iRet = LOAD_SUCCESS;
	
	FILE *pf = fopen(pcFileName,"rb");
	if(!pf)
	{ 
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not open file \"" << pcFileName << "\"." << "\n";
		return LOAD_FAIL;
	}
	
	unsigned int uiBufLen = fread(m_puiDaten, sizeof(unsigned int), iSize, pf);
	if(!uiBufLen)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not read file \"" << pcFileName << "\"." << "\n";
	}
	if(uiBufLen!=(unsigned int)iSize)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Buffer size (" << uiBufLen << " ints) != TOF size (" << iSize << " ints)." << "\n";
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
// pix start x, pix ende x, pix start y, pix end y, folie (n=0..3; 0=0.., 1=32.., 2=128, 3=160), wievielte tof-image dieser folie (0..15), wenn 0, dann 16 auch dazuzählen
void TofImage::GetROI(int iStartX, int iEndX, int iStartY, int iEndY, int iFolie, int iTimechannel, TmpImage *pImg) const
{
	if(!pImg) return;
	
	Config_TofLoader::CheckArguments(&iStartX, &iEndX, &iStartY, &iEndY, &iFolie, &iTimechannel);

	int iBildBreite = abs(iEndX-iStartX);
	int iBildHoehe = abs(iEndY-iStartY);
	
	unsigned int *puiWave = new unsigned int[iBildHoehe*iBildBreite];
	if(puiWave==NULL) 
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line " << __LINE__ << ")!\n";
		return;
	}
	
	pImg->Clear();
	pImg->m_iW = iBildBreite;
	pImg->m_iH = iBildHoehe;
	pImg->m_puiDaten = puiWave;

	for(int iY=iStartY; iY<iEndY; ++iY)
		for(int iX=iStartX; iX<iEndX; ++iX)
			puiWave[(iX-iStartX) + (iY-iStartY)*iBildBreite] = GetData(iFolie,iTimechannel,iX,iY);
}

// TOF-Graph
// pix start x, pix ende x, pix start y, pix end y, folie (n=0..3; 0=0.., 1=32.., 2=128, 3=160)
// alle Pixel eines Kanals addieren
void TofImage::GetGraph(int iStartX, int iEndX, int iStartY, int iEndY, int iFolie, TmpGraph* pGraph) const
{
	if(!pGraph) return;
	
	Config_TofLoader::CheckArguments(&iStartX, &iEndX, &iStartY, &iEndY, &iFolie);
	unsigned int *puiWave = new unsigned int[Config_TofLoader::IMAGES_PER_FOIL];
	
	pGraph->m_iW = Config_TofLoader::IMAGES_PER_FOIL;
	pGraph->m_puiDaten = puiWave;

	for(int iZ0=0; iZ0<Config_TofLoader::IMAGES_PER_FOIL; ++iZ0)
	{
		unsigned int uiSummedVal=0;
		for(int iY=iStartY; iY<iEndY; ++iY)
			for(int iX=iStartX; iX<iEndX; ++iX)
				uiSummedVal += GetData(iFolie, iZ0, iX, iY);
			
		puiWave[iZ0]=uiSummedVal;
	}
}

void TofImage::GetTotalGraph(int iStartX, int iEndX, int iStartY, int iEndY, double dPhaseShift, TmpGraph* pGraph) const
{
	if(!pGraph) return;
	
	Config_TofLoader::CheckArguments(&iStartX, &iEndX, &iStartY, &iEndY);
	unsigned int *puiWave = new unsigned int[Config_TofLoader::IMAGES_PER_FOIL];
	
	pGraph->m_iW = Config_TofLoader::IMAGES_PER_FOIL;
	pGraph->m_puiDaten = puiWave;

	// Zeitkanäle
	for(int iZ0=0; iZ0<Config_TofLoader::IMAGES_PER_FOIL; ++iZ0)
	{
		unsigned int uiSummedVal=0;
		for(int iY=iStartY; iY<iEndY; ++iY)
		{
			for(int iX=iStartX; iX<iEndX; ++iX)
			{
				// Folien
				for(int iFolie=0; iFolie<Config_TofLoader::FOIL_COUNT; ++iFolie)
				{
					int iShift = iZ0 + int(dPhaseShift*double(iFolie));
					if(iShift>=Config_TofLoader::IMAGES_PER_FOIL)
						iShift%=Config_TofLoader::IMAGES_PER_FOIL;
						
					uiSummedVal += GetData(iFolie, iShift, iX, iY);
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
	pImg->m_iW = Config_TofLoader::GetImageWidth();
	pImg->m_iH = Config_TofLoader::GetImageHeight();
	pImg->m_puiDaten = new unsigned int[Config_TofLoader::GetImageWidth()*Config_TofLoader::GetImageHeight()];
	if(pImg->m_puiDaten==NULL) 
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line " << __LINE__ << ")!\n";
		return;
	}
	memset(pImg->m_puiDaten,0,sizeof(int)*pImg->m_iW*pImg->m_iH);
	
	for(int iFolie=0; iFolie<Config_TofLoader::FOIL_COUNT; ++iFolie)
		for(int iZ0=0; iZ0<Config_TofLoader::IMAGES_PER_FOIL; ++iZ0)
			for(int iY=0; iY<Config_TofLoader::GetImageHeight(); ++iY)
				for(int iX=0; iX<Config_TofLoader::GetImageWidth(); ++iX)
					pImg->m_puiDaten[iY*Config_TofLoader::GetImageWidth()+iX] += GetData(iFolie,iZ0,iX,iY);
}

// Alle Folien, die in iBits als aktiv markiert sind, addieren;
// dasselbe fuer die Kanaele
void TofImage::AddFoils(int iBits, int iZeitKanaeleBits, TmpImage *pImg) const
{
	if(!pImg) return;
	
	bool bFolieAktiv[Config_TofLoader::FOIL_COUNT],
		bKanaeleAktiv[Config_TofLoader::IMAGES_PER_FOIL];
	
	for(int i=0; i<Config_TofLoader::FOIL_COUNT; ++i)
	{
		if(iBits & (1<<i)) bFolieAktiv[i]=true;
		else bFolieAktiv[i]=false;
	}
	
	for(int i=0; i<Config_TofLoader::IMAGES_PER_FOIL; ++i)
	{
		if(iZeitKanaeleBits & (1<<i)) bKanaeleAktiv[i]=true;
		else bKanaeleAktiv[i]=false;		
	}
	
	unsigned int uiAusgabe[Config_TofLoader::GetImageHeight()][Config_TofLoader::GetImageWidth()];
	memset(uiAusgabe,0,Config_TofLoader::GetImageHeight()*Config_TofLoader::GetImageWidth()*sizeof(int));
	
	unsigned int *puiWave = new unsigned int[Config_TofLoader::GetImageWidth()*Config_TofLoader::GetImageHeight()];
	if(puiWave==NULL) 
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line " << __LINE__ << ")!\n";
		return;
	}
	
	pImg->Clear();
	pImg->m_iW = Config_TofLoader::GetImageWidth();
	pImg->m_iH = Config_TofLoader::GetImageHeight();
	pImg->m_puiDaten = puiWave;

	for(int iFolie=0; iFolie<Config_TofLoader::FOIL_COUNT; ++iFolie)
	{
		if(!bFolieAktiv[iFolie]) continue;

		for(int iZ0=0; iZ0<Config_TofLoader::IMAGES_PER_FOIL; ++iZ0)
		{
			if (!bKanaeleAktiv[iZ0]) continue;
			for(int iY=0; iY<Config_TofLoader::GetImageHeight(); ++iY)
				for(int iX=0; iX<Config_TofLoader::GetImageWidth(); ++iX)
					uiAusgabe[iY][iX] += GetData(iFolie,iZ0,iX,iY);
		}
	}
	
	for(int iY=0; iY<Config_TofLoader::GetImageHeight(); ++iY)
		for(int iX=0; iX<Config_TofLoader::GetImageWidth(); ++iX)
				puiWave[iY*Config_TofLoader::GetImageWidth()+iX] = uiAusgabe[iY][iX];
}

// Alle Kanaele, die im bool-Feld gesetzt sind, addieren
void TofImage::AddFoils(const bool *pbKanaele, TmpImage *pImg) const
{
	if(!pImg) return;
	
	unsigned int uiAusgabe[Config_TofLoader::GetImageHeight()][Config_TofLoader::GetImageWidth()];
	memset(uiAusgabe,0,Config_TofLoader::GetImageHeight()*Config_TofLoader::GetImageWidth()*sizeof(int));
	
	unsigned int *puiWave = new unsigned int[Config_TofLoader::GetImageWidth()*Config_TofLoader::GetImageHeight()];
	if(puiWave==NULL) 
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line " << __LINE__ << ")!\n";
		return;
	}
	
	pImg->Clear();
	pImg->m_iW = Config_TofLoader::GetImageWidth();
	pImg->m_iH = Config_TofLoader::GetImageHeight();
	pImg->m_puiDaten = puiWave;

	for(int iFolie=0; iFolie<Config_TofLoader::FOIL_COUNT; ++iFolie)
	{
		for(int iZ0=0; iZ0<Config_TofLoader::IMAGES_PER_FOIL; ++iZ0)
		{
			if(!pbKanaele[iFolie*Config_TofLoader::IMAGES_PER_FOIL + iZ0]) continue;
			
			for(int iY=0; iY<Config_TofLoader::GetImageHeight(); ++iY)
				for(int iX=0; iX<Config_TofLoader::GetImageWidth(); ++iX)
					uiAusgabe[iY][iX] += GetData(iFolie, iZ0, iX, iY);
		}
	}
	
	for(int iY=0; iY<Config_TofLoader::GetImageHeight(); ++iY)
		for(int iX=0; iX<Config_TofLoader::GetImageWidth(); ++iX)
				puiWave[iY*Config_TofLoader::GetImageWidth()+iX] = uiAusgabe[iY][iX];
}

// Alle Phasenbilder, die im bool-Feld gesetzt sind, addieren
void TofImage::AddPhases(const bool *pbFolien, TmpImage *pImg) const
{
	if(pImg==NULL) return;
	double *pdWave = new double[Config_TofLoader::GetImageWidth()*Config_TofLoader::GetImageHeight()];
	if(pdWave==NULL) 
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line " << __LINE__ << ")!\n";
		return;
	}

	pImg->Clear();
	pImg->m_iW = Config_TofLoader::GetImageWidth();
	pImg->m_iH = Config_TofLoader::GetImageHeight();
	pImg->m_pdDaten = pdWave;
	
	memset(pdWave, 0, sizeof(double)*pImg->m_iW*pImg->m_iH);
	
	for(int iFolie=0; iFolie<Config_TofLoader::FOIL_COUNT; ++iFolie)
	{
		if(!pbFolien[iFolie]) continue;
			
		TmpImage tmpimg;
		GetPhaseGraph(iFolie, &tmpimg);
	
		pImg->Add(tmpimg);
	}
	
	for(int iY=0; iY<pImg->m_iH; ++iY)
		for(int iX=0; iX<pImg->m_iW; ++iX)
			pdWave[iY*pImg->m_iW + iX] = fmod(pdWave[iY*pImg->m_iW + iX], 360.);	// DEG verwenden!
}

// Alle Kontrastbilder, die im bool-Feld gesetzt sind, addieren
void TofImage::AddContrasts(const bool *pbFolien, TmpImage *pImg) const
{
	if(pImg==NULL) return;
	double *pdWave = new double[Config_TofLoader::GetImageWidth()*Config_TofLoader::GetImageHeight()];
	if(pdWave==NULL) 
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line " << __LINE__ << ")!\n";
		return;
	}

	pImg->Clear();
	pImg->m_iW = Config_TofLoader::GetImageWidth();
	pImg->m_iH = Config_TofLoader::GetImageHeight();
	pImg->m_pdDaten = pdWave;
	
	memset(pdWave, 0, sizeof(double)*pImg->m_iW*pImg->m_iH);
	
	for(int iFolie=0; iFolie<Config_TofLoader::FOIL_COUNT; ++iFolie)
	{
		if(!pbFolien[iFolie]) continue;
			
		TmpImage tmpimg;
		GetContrastGraph(iFolie, &tmpimg);
	
		pImg->Add(tmpimg);
	}
}

// Für Kalibrierungsdiagramm
void TofImage::GetPhaseGraph(int iFoil, TmpImage *pImg, bool bInDeg) const
{
	GetPhaseGraph(iFoil, pImg, 0, Config_TofLoader::GetImageWidth(), 0, Config_TofLoader::GetImageHeight(), bInDeg);
}

void TofImage::GetPhaseGraph(int iFolie, TmpImage *pImg, int iStartX, int iEndX, int iStartY, int iEndY, bool bInDeg) const
{
	if(pImg==NULL) return;
	Config_TofLoader::CheckArguments(&iStartX, &iEndX, &iStartY, &iEndY);

	pImg->Clear();
	pImg->m_iW = abs(iEndX-iStartX);
	pImg->m_iH = abs(iEndY-iStartY);
	
	const int XSIZE = Config_TofLoader::iPhaseBlockSize[0],
		  YSIZE = Config_TofLoader::iPhaseBlockSize[1];	
	
	double *pdWave = new double[(pImg->m_iW+XSIZE) * (pImg->m_iH+YSIZE)];
	if(pdWave==NULL) 
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line " << __LINE__ << ")!\n";
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
	GetContrastGraph(iFoil, pImg, 0, Config_TofLoader::GetImageWidth(), 0, Config_TofLoader::GetImageHeight());
}

void TofImage::GetContrastGraph(int iFoil, TmpImage *pImg, int iStartX, int iEndX, int iStartY, int iEndY) const
{
	if(pImg==NULL) return;
	Config_TofLoader::CheckArguments(&iStartX, &iEndX, &iStartY, &iEndY);

	pImg->Clear();
	pImg->m_iW = iEndX-iStartX;
	pImg->m_iH = iEndY-iStartY;
	
	const int XSIZE = Config_TofLoader::iContrastBlockSize[0],
		  YSIZE = Config_TofLoader::iContrastBlockSize[1];	
	
	double *pdWave = new double[(pImg->m_iW+XSIZE) * (pImg->m_iH+YSIZE)];
	if(pdWave==NULL) 
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line " << __LINE__ << ")!\n";
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
					pdWave[(iY-iStartY+i)*pImg->m_iW+(iX-iStartX+j)] = dContrast;
		}
}

unsigned int TofImage::GetCounts() const
{
	return GetCounts(0, Config_TofLoader::GetImageWidth(), 0, Config_TofLoader::GetImageHeight());
}

unsigned int TofImage::GetCounts(int iStartX, int iEndX, int iStartY, int iEndY) const
{
	Config_TofLoader::CheckArguments(&iStartX, &iEndX, &iStartY, &iEndY);
	
	TmpImage img;
	GetOverview(&img);
	
	unsigned int uiCnt = 0;
	for(int iY=iStartY; iY<iEndY; ++iY)
		for(int iX=iStartX; iX<iEndX; ++iX)
			uiCnt += img.GetData(iX, iY);
	return uiCnt;
}


/////////////////////////////////////////

TmpImage TofImage::GetROI(int iStartX, int iEndX, int iStartY, int iEndY, int iFolie, int iZ) const
{
	TmpImage img;
	GetROI(iStartX, iEndX, iStartY, iEndY, iFolie, iZ, &img);
	return img;
}

TmpGraph TofImage::GetGraph(int iStartX, int iEndX, int iStartY, int iEndY, int iFolie) const
{
	TmpGraph graph;
	GetGraph(iStartX, iEndX, iStartY, iEndY, iFolie, &graph);
	return graph;
}

TmpGraph TofImage::GetTotalGraph(int iStartX, int iEndX, int iStartY, int iEndY, double dPhaseShift) const
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

TmpImage TofImage::GetPhaseGraph(int iFolie, int iStartX, int iEndX, int iStartY, int iEndY, bool bInDeg) const
{
	TmpImage img;
	GetPhaseGraph(iFolie, &img, iStartX, iEndX, iStartY, iEndY, bInDeg);
	return img;
}

TmpImage TofImage::GetContrastGraph(int iFolie, int iStartX, int iEndX, int iStartY, int iEndY) const
{
	TmpImage img;
	GetContrastGraph(iFolie, &img, iStartX, iEndX, iStartY, iEndY);
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

////////////////// TOF //////////////////



////////////////// PAD //////////////////
PadImage::PadImage(const char *pcFileName, bool bExternalMem) : m_iMin(0),m_iMax(0), m_bExternalMem(bExternalMem)
{
	m_puiDaten = 0;
	
	if(!m_bExternalMem)
	{
		m_puiDaten = new unsigned int[GetPadSize()];
		if(m_puiDaten==NULL)
		{
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "Loader: Could not allocate memory (line " << __LINE__ << ")!\n";
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
	
	m_puiDaten = new unsigned int[GetPadSize()];
	if(m_puiDaten == NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line " << __LINE__ << ")!\n";
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

int PadImage::GetPadSize() const
{
	int iSize = Config_TofLoader::GetImageHeight()*Config_TofLoader::GetImageWidth();
	return iSize;
}

void PadImage::SetExternalMem(void* pvDaten) 
{ 
	if(!m_bExternalMem) return;
	
	m_puiDaten = (unsigned int*)pvDaten; 
	//UpdateRange();
}

void PadImage::UpdateRange()
{
	m_iMin=std::numeric_limits<double>::max();
	m_iMax=0;
	for(int iY=0; iY<Config_TofLoader::GetImageHeight(); ++iY)
	{
		for(int iX=0; iX<Config_TofLoader::GetImageWidth(); ++iX)
		{
			m_iMin = (m_iMin<int(GetData(iX,iY)))?m_iMin:GetData(iX,iY);
			m_iMax = (m_iMax>int(GetData(iX,iY)))?m_iMax:GetData(iX,iY);
		}
	}
}

int PadImage::LoadMem(const unsigned int *puiBuf, unsigned int uiBufLen)
{
	if(uiBufLen!=(unsigned int)Config_TofLoader::GetImageHeight()*Config_TofLoader::GetImageWidth())
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Buffer size (" << uiBufLen << " ints) != PAD size (" << Config_TofLoader::GetImageHeight()*Config_TofLoader::GetImageWidth() << " ints)." << "\n";
		return LOAD_SIZE_MISMATCH;
	}
	
	memcpy(m_puiDaten, puiBuf, sizeof(int)*Config_TofLoader::GetImageHeight()*Config_TofLoader::GetImageWidth());
	
	// falls PowerPC, ints von little zu big endian konvertieren
#ifdef __BIG_ENDIAN__
		for(int iY=0; iY<Config_TofLoader::GetImageHeight(); ++iY)
			for(int iX=0; iX<Config_TofLoader::GetImageWidth(); ++iX)
				GetData(iX,iY) = endian_swap(GetData(iX,iY));
#endif
	
	UpdateRange();
	return LOAD_SUCCESS;
}

int PadImage::LoadFile(const char *pcFileName)
{
	int iRet = LOAD_SUCCESS;
	
	FILE *pf = fopen(pcFileName,"rb");
	if(!pf)
	{ 
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not open file \"" << pcFileName << "\"." << "\n";
		return LOAD_FAIL;
	}
	
	unsigned int uiBufLen = fread(m_puiDaten, sizeof(unsigned int),Config_TofLoader::GetImageHeight()*Config_TofLoader::GetImageWidth(),pf);
	if(!uiBufLen)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not read file \"" << pcFileName << "\"." << "\n";
	}
	
	if(uiBufLen!=(unsigned int)Config_TofLoader::GetImageHeight()*Config_TofLoader::GetImageWidth())
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Buffer size (" << uiBufLen << " ints) != PAD size (" << Config_TofLoader::GetImageHeight()*Config_TofLoader::GetImageWidth() << " ints)." << "\n";
		iRet = LOAD_SIZE_MISMATCH;
	}	
	fclose(pf);
	
// falls PowerPC, ints von little zu big endian konvertieren
#ifdef __BIG_ENDIAN__
	for(int iY=0; iY<Config_TofLoader::GetImageHeight(); ++iY)
		for(int iX=0; iX<Config_TofLoader::GetImageWidth(); ++iX)
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

	for(int iY=0; iY<Config_TofLoader::GetImageHeight(); ++iY)
	{
		for(int iX=0; iX<Config_TofLoader::GetImageWidth(); ++iX)
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
	if(m_puiDaten==NULL) return 0;
	
	if(iX>=0 && iX<Config_TofLoader::GetImageWidth() && iY>=0 && iY<Config_TofLoader::GetImageHeight())
		return m_puiDaten[iY*Config_TofLoader::GetImageWidth() + iX];
	else 
		return 0;
}

unsigned int PadImage::GetCounts() const
{
	return GetCounts(0, Config_TofLoader::GetImageWidth(), 0, Config_TofLoader::GetImageHeight());
}

unsigned int PadImage::GetCounts(int iStartX, int iEndX, int iStartY, int iEndY) const
{
	Config_TofLoader::CheckArguments(&iStartX, &iEndX, &iStartY, &iEndY);
	
	unsigned int uiCnt = 0;
	for(int iY=iStartY; iY<iEndY; ++iY)
		for(int iX=iStartX; iX<iEndX; ++iX)
			uiCnt += GetData(iX, iY);

	return uiCnt;
}
////////////////// PAD //////////////////  



////////////////// TmpImage /////////////
TmpImage::TmpImage() : m_iW(0), m_iH(0), m_puiDaten(NULL), m_pdDaten(NULL), m_dMin(0), m_dMax(0)
{
}

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
			logger << "Loader: Could not allocate memory (line " << __LINE__ << ")!\n";
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
			logger << "Loader: Could not allocate memory (line " << __LINE__ << ")!\n";
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
	if(iX>=0 && iX<m_iW && iY>=0 && iY<m_iH)
	{
		if(m_puiDaten)
			return double(m_puiDaten[iY*m_iW + iX]);
		else if(m_pdDaten)
			return m_pdDaten[iY*m_iW + iX];
	}
	return 0.;
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
	
int TmpImage::GetWidth() const { return m_iW; }
int TmpImage::GetHeight() const { return m_iH; }

void TmpImage::Add(const TmpImage& tmp)
{
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
				m_dMin = (m_dMin<m_puiDaten[m_iW*iY+iX])?m_dMin:m_puiDaten[m_iW*iY+iX];
				m_dMax = (m_dMax>m_puiDaten[m_iW*iY+iX])?m_dMax:m_puiDaten[m_iW*iY+iX];
			}
			else if(m_pdDaten)
			{
				m_dMin = (m_dMin<m_pdDaten[m_iW*iY+iX])?m_dMin:m_pdDaten[m_iW*iY+iX];
				m_dMax = (m_dMax>m_pdDaten[m_iW*iY+iX])?m_dMax:m_pdDaten[m_iW*iY+iX];
			}
		}
	}
}

bool TmpImage::WriteXML(const char* pcFileName) const
{
	std::ofstream ofstr(pcFileName);
	if(!ofstr.is_open()) 
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not open file \"" << pcFileName << "\" for writing.\n";
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
	m_iW = Config_TofLoader::GetImageWidth();
	m_iH = Config_TofLoader::GetImageHeight();
	m_dMin = pPad->m_iMin;
	m_dMax = pPad->m_iMax;
	
	m_puiDaten = new unsigned int[Config_TofLoader::GetImageWidth()*Config_TofLoader::GetImageHeight()];
	if(m_puiDaten==NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line " << __LINE__ << ")!\n";
		return;
	}
	memcpy(m_puiDaten, pPad->m_puiDaten, Config_TofLoader::GetImageWidth()*Config_TofLoader::GetImageHeight()*sizeof(int));
}


//////////////////////// TmpGraph ////////////////////////////

TmpGraph::TmpGraph()
{
	m_iW = 0;
	m_puiDaten = NULL;
}

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

#ifdef USE_MINUIT
// ************************** Zeug für Minuit **************************
// Modellfunktion für sin-Fit
class Sinus : public ROOT::Minuit2::FCNBase
{
	protected:
		double *m_pdy;			// experimentelle Werte
 		double *m_pddy;			// Standardabweichungen
		int m_iNum;			// Anzahl der Werte
	
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
				
		// soll Chi^2 zurückgeben
		double operator()(const std::vector<double>& params) const
		{
			double dphase = params[0];
			double damp = params[1];
			double doffs = params[2];
			double dscale = /*params[3]*/ 2.*M_PI/double(Config_TofLoader::GetImagesPerFoil());	// fest
			
			// erzwingt, dass Amplituden-Fitparameter nicht negativ gewählt wird
			if(damp<0.) return std::numeric_limits<double>::max();

			double dchi2 = 0.;
			for(int i=0; i<m_iNum; ++i)
			{
				double dAbweichung = m_pddy[i];
				//if(fabs(dAbweichung) < std::numeric_limits<double>::epsilon())
				//	dAbweichung = std::numeric_limits<double>::epsilon();
				
				double d = (m_pdy[i] - (damp*sin(double(i)*dscale + dphase)+doffs)) / dAbweichung;
				dchi2 += d*d;
			}
			return dchi2;
		}
		
		double Up() const
		{
			return 1.;
		}
		
		const double* GetValues() const { return m_pdy; }
		const double* GetDeviations() const { return m_pddy; }
				
		void SetValues(int iSize, const double* pdy)
		{
			Clear();
			m_iNum = iSize;
			m_pdy = new double[iSize];
			m_pddy = new double[iSize];
			
			for(int i=0; i<iSize; ++i)
			{
				m_pdy[i] = pdy[i];		// Wert
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

bool TmpGraph::IsLowerThan(int iTotal) const
{
	unsigned int uiSum;
	for(int i=0; i<m_iW; ++i)
		uiSum += GetData(i);
	
	return uiSum < iTotal;
}

bool TmpGraph::FitSinus(double &dPhase, double &dScale, double &dAmp, double &dOffs) const
{
	if(m_iW<=0) return false;
	dScale = 2.*M_PI/double(Config_TofLoader::GetImagesPerFoil()); 	// Scale-Parameter fix

	double dMaxVal=GetMax(), dMinVal=GetMin();
	dOffs = dMinVal + (dMaxVal-dMinVal)/2.;		// Hint-Werte
	dAmp = (dMaxVal-dMinVal)/2.;			// Hint-Werte
	
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
	
	ROOT::Minuit2::MnMigrad migrad(fkt, upar);
	ROOT::Minuit2::FunctionMinimum mini = migrad();
	
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
	if(dPhase!=dPhase || dAmp!=dAmp || dOffs!=dOffs)
	{
		//logger.SetCurLogLevel(LOGLEVEL_WARN);
		//logger << "Loader: Could not find correct fit." << "\n";
		return false;
	}
	return true;
}
// ***************************************************************************
#else
bool TmpGraph::FitSinus(double &dPhase, double &dScale, double &dAmp, double &dOffs) const
{
	return false;
}
#endif
