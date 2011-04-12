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

#include <iostream>
#include <fstream>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <vector>
#include <string.h>
#include <limits>

#ifdef USE_MINUIT
	#include <Minuit2/FCNBase.h>
	#include <Minuit2/FunctionMinimum.h>
	#include <Minuit2/MnMigrad.h>
	#include <Minuit2/MnUserParameters.h>
	#include <Minuit2/MnPrint.h>
#endif

#ifdef IGOR_PLUGIN
	#include <XOPStandardHeaders.h>
#endif

//////////////////////////// Konfiguration ///////////////////////////
// Default-Werte
int Config_TofLoader::FOIL_COUNT = 4;
int Config_TofLoader::IMAGES_PER_FOIL = 16;
int Config_TofLoader::IMAGE_WIDTH = 128;
int Config_TofLoader::IMAGE_HEIGHT = 128;
int Config_TofLoader::IMAGE_COUNT = 196;
static const int g_iDefaultFoilBegin[] = {0, 32, 128, 160};
int *Config_TofLoader::piFoilBegin = 0 /*{0, 32, 128, 160}*/;

int Config_TofLoader::iPhaseBlockSize[2] = {1, 2};
int Config_TofLoader::iContrastBlockSize[2] = {1, 2};

double Config_TofLoader::LOG_LOWER_RANGE = -0.5;


void Config_TofLoader::Init()
{
#ifdef __BIG_ENDIAN__
	std::cerr << "This is a PowerPC (big endian)." << std::endl;
#endif

	Deinit();

// Cascade-Qt-Client lädt Einstellungen über XML-Datei
#ifdef __CASCADE_QT_CLIENT__	
	IMAGE_COUNT = Config::GetSingleton()->QueryInt("/cascade_config/tof_file/image_count", IMAGE_COUNT);
	FOIL_COUNT = Config::GetSingleton()->QueryInt("/cascade_config/tof_file/foil_count", FOIL_COUNT);
	IMAGES_PER_FOIL = Config::GetSingleton()->QueryInt("/cascade_config/tof_file/images_per_foil", IMAGES_PER_FOIL);
	IMAGE_WIDTH = Config::GetSingleton()->QueryInt("/cascade_config/tof_file/image_width", IMAGE_WIDTH);
	IMAGE_HEIGHT = Config::GetSingleton()->QueryInt("/cascade_config/tof_file/image_height", IMAGE_HEIGHT);
	
	piFoilBegin = new int[FOIL_COUNT];
	for(int i=0; i<FOIL_COUNT; ++i)
	{
		char pcStr[256];
		sprintf(pcStr, "/cascade_config/tof_file/foil_%d_start", i+1);
		piFoilBegin[i] = Config::GetSingleton()->QueryInt(pcStr, g_iDefaultFoilBegin[i]);
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
		piFoilBegin[i] = g_iDefaultFoilBegin[i];
	
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

void Config_TofLoader::SetFoilBegin(int iFoil, int iOffs)
{
	if(iFoil<0 || iFoil>=FOIL_COUNT) return;
	
	piFoilBegin[iFoil] = iOffs;
}
//////////////////////////////////////////////////////////////////////////////////////////

bool Config_TofLoader::GuessConfigFromSize(int iLen, bool bIsTof, bool bFirstCall)
{
	if(bFirstCall) std::cerr << "Warning: Guessing Configuration." << std::endl;

	static const int MIN_SHIFT = 6;		// 64
 	static const int MAX_SHIFT = 10;	// 1024
	static const int MIN_LEN = 1<<MIN_SHIFT;
	static const int MAX_LEN = 1<<MAX_SHIFT;	
	
	const int iKnownX[] = 	{64,  128};
	const int iKnownY[] = 	{128, 128};
	const int iKnownCnt[] = {196, 128};

	if(bIsTof)	// TOF
	{
		bool bFound=false;
	
		// bekannte Konfigurationen absuchen
		for(int i=0; i<sizeof(iKnownCnt)/sizeof(int); ++i)
		{
			if(iKnownX[i]*iKnownY[i]*iKnownCnt[i] != iLen) continue;
			GuessConfigFromSize(iKnownX[i]*iKnownY[i],false,false);		// eigentlich unnötig, nur wegen cerr-Ausgabe
			
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
				
				if(GuessConfigFromSize(iLen/iImgCnt, false, false))
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
				
				if(GuessConfigFromSize(iLen/iImgCnt, false, false))
				{
					bFound = true;
					IMAGE_COUNT = iImgCnt;
					break;
				}
			}			
		}
		
		if(bFound)
		{
			std::cerr << "guessing image count: " << IMAGE_COUNT << std::endl;
		}
		return bFound;
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
			std::cerr << "guessing image width: " << IMAGE_WIDTH << std::endl;
			std::cerr << "guessing image height: " << IMAGE_HEIGHT << std::endl;
		}		
		return bFound;
	}
}

//////////////////////////////////////////////////////////////////////

// wandle Big-Endian <-> Little-Endian um (für Mac)
static inline unsigned int endian_swap(unsigned int x)
{
	return (x>>24) | ((x<<8) & 0x00FF0000) | ((x>>8) & 0x0000FF00) | (x<<24);
}

// Wenn IGOR: Eine Wave-Matrix erzeugen und einen Pointer auf ihr internes Array zurueckgeben
static unsigned int* CreateUIntWave(const char* pcBaseName, int iDimX, int iDimY)
{
#ifdef IGOR_PLUGIN
	if(FetchWave(pcBaseName)!=NULL)
	{
		XOPNotice("Kann UInt-Wave nicht erzeugen, da sie bereits existiert.\r");
		return NULL;
	}

	waveHndl wavMatrix;
	long lDimensions[MAX_DIMENSIONS+1] = {iDimX,iDimY,0};
	
	// Wave-Matrix erstellen
	MDMakeWave(&wavMatrix, pcBaseName, NULL, lDimensions, NT_I32|NT_UNSIGNED,1);
	//MDStoreDPDataInNumericWave(wavMatrix, dTest);

	long lDataOffset;
	MDAccessNumericWaveData(wavMatrix, kMDWaveAccessMode0, &lDataOffset);
	
	MoveLockHandle(wavMatrix);
	unsigned int* puiRet = (unsigned int*)((char*)(*wavMatrix)+lDataOffset);
	if(puiRet==NULL)
	{
		XOPNotice("Kann UInt-Wave nicht erstellen.\r");
		return NULL;
	}
	return puiRet;
	
// Ansonsten einfach Array anlegen
#else
	if(iDimY<=0) iDimY=1;
	if(iDimX<=0) iDimX=1;
	return new unsigned int[iDimY*iDimX];
#endif
}

// Wenn IGOR: Eine Wave-Matrix erzeugen und einen Pointer auf ihr internes Array zurueckgeben
static double* CreateDoubleWave(const char* pcBaseName, int iDimX, int iDimY)
{
#ifdef IGOR_PLUGIN
	if(FetchWave(pcBaseName)!=NULL)
	{
		XOPNotice("Kann Double-Wave nicht erzeugen, da sie bereits existiert.\r");
		return NULL;
	}

	waveHndl wavMatrix;
	long lDimensions[MAX_DIMENSIONS+1] = {iDimX,iDimY,0};
	
	// Wave-Matrix erstellen
	MDMakeWave(&wavMatrix, pcBaseName, NULL, lDimensions, NT_FP64, 1);
	//MDStoreDPDataInNumericWave(wavMatrix, dTest);

	long lDataOffset;
	MDAccessNumericWaveData(wavMatrix, kMDWaveAccessMode0,&lDataOffset);
	
	MoveLockHandle(wavMatrix);
	double* puiRet = (double*)((char*)(*wavMatrix)+lDataOffset);
	if(puiRet==NULL)
	{
		XOPNotice("Kann Double-Wave nicht erstellen.\r");
		return NULL;
	}
	return puiRet;
	
// Ansonsten einfach Array anlegen
#else
	if(iDimY<=0) iDimY=1;
	if(iDimX<=0) iDimX=1;
	return new double[iDimY*iDimX];
#endif
}

////////////////// TOF ////////////////// 

void TofImage::Clear(void)
{
	if(m_puiDaten) { delete[] m_puiDaten; m_puiDaten=NULL; }
}

unsigned int& TofImage::GetData(int iBild, int iX, int iY)
{
	static unsigned int iDummy=0;
	if(m_puiDaten && iBild>=0 && iBild<Config_TofLoader::IMAGE_COUNT && iX>=0 && iX<Config_TofLoader::IMAGE_WIDTH && iY>=0 && iY<Config_TofLoader::IMAGE_HEIGHT)
		return m_puiDaten[iBild*Config_TofLoader::IMAGE_WIDTH*Config_TofLoader::IMAGE_HEIGHT + iY*Config_TofLoader::IMAGE_WIDTH + iX];
	return iDummy; // Referenz auf Dummy zurückgeben
}

unsigned int TofImage::GetData(int iFoil, int iTimechannel, int iX, int iY)
{
	int iZ=0;
	switch(iFoil)
	{
		case 0: iZ=Config_TofLoader::piFoilBegin[0]; break;
		case 1: iZ=Config_TofLoader::piFoilBegin[1]; break;
		case 2: iZ=Config_TofLoader::piFoilBegin[2]; break;
		case 3: iZ=Config_TofLoader::piFoilBegin[3]; break;
	};
	
	iZ += iTimechannel;
	if(iTimechannel!=0)
		return GetData(iZ,iX,iY);
	else
		return GetData(iZ,iX,iY)+GetData(iZ+Config_TofLoader::IMAGES_PER_FOIL,iX,iY);
}

unsigned int* TofImage::GetRawData(void) const
{
	return m_puiDaten;
}

TofImage::TofImage(const char *pcFileName)
{
	m_puiDaten = new unsigned int[Config_TofLoader::IMAGE_COUNT*Config_TofLoader::IMAGE_HEIGHT*Config_TofLoader::IMAGE_WIDTH];
	
	if(pcFileName!=NULL) LoadFile(pcFileName);
	else memset(m_puiDaten,0,Config_TofLoader::IMAGE_COUNT*Config_TofLoader::IMAGE_HEIGHT*Config_TofLoader::IMAGE_WIDTH*sizeof(int));
}

TofImage::~TofImage()
{
	Clear();
}

int TofImage::LoadMem(const unsigned int *puiBuf, unsigned int uiBufLen)
{
	if(uiBufLen!=(unsigned int)Config_TofLoader::IMAGE_COUNT*Config_TofLoader::IMAGE_HEIGHT*Config_TofLoader::IMAGE_WIDTH)
	{
		std::cerr << "Error: Buffer size (" << uiBufLen << " ints) != TOF size (" << Config_TofLoader::IMAGE_COUNT*Config_TofLoader::IMAGE_HEIGHT*Config_TofLoader::IMAGE_WIDTH << " ints)." << std::endl;
		return LOAD_SIZE_MISMATCH;
	}
	
	memcpy(m_puiDaten, puiBuf, sizeof(int)*Config_TofLoader::IMAGE_COUNT*Config_TofLoader::IMAGE_HEIGHT*Config_TofLoader::IMAGE_WIDTH);
	
// falls PowerPC, ints von little zu big endian konvertieren
#ifdef __BIG_ENDIAN__
	for(int iZ=0; iZ<Config_TofLoader::IMAGE_COUNT; ++iZ)
		for(int iY=0; iY<Config_TofLoader::IMAGE_HEIGHT; ++iY)
			for(int iX=0; iX<Config_TofLoader::IMAGE_WIDTH; ++iX)
				GetData(iZ,iX,iY) = endian_swap(GetData(iZ,iX,iY));
#endif	
	return LOAD_SUCCESS;	
}

int TofImage::LoadFile(const char *pcFileName)
{
	int iRet = LOAD_SUCCESS;
	
	FILE *pf = fopen(pcFileName,"rb");
	if(!pf)
	{ 
		std::cerr << "Error: Could not open file \"" << pcFileName << "\"." << std::endl;
		return LOAD_FAIL;
	}
	
	unsigned int uiBufLen=fread(m_puiDaten, sizeof(unsigned int),Config_TofLoader::IMAGE_COUNT*Config_TofLoader::IMAGE_HEIGHT*Config_TofLoader::IMAGE_WIDTH,pf);
	if(!uiBufLen)
	{
		std::cerr << "Error: Could not read file \"" << pcFileName << "\"." << std::endl;
	}
	if(uiBufLen!=(unsigned int)Config_TofLoader::IMAGE_COUNT*Config_TofLoader::IMAGE_HEIGHT*Config_TofLoader::IMAGE_WIDTH)
	{
		std::cerr << "Error: Buffer size (" << uiBufLen << " ints) != TOF size (" << Config_TofLoader::IMAGE_COUNT*Config_TofLoader::IMAGE_HEIGHT*Config_TofLoader::IMAGE_WIDTH << " ints)." << std::endl;
		iRet = LOAD_SIZE_MISMATCH;
	}	
	
	fclose(pf);
	
// falls PowerPC, ints von little zu big endian konvertieren
#ifdef __BIG_ENDIAN__
	for(int iZ=0; iZ<Config_TofLoader::IMAGE_COUNT; ++iZ)
		for(int iY=0; iY<Config_TofLoader::IMAGE_HEIGHT; ++iY)
			for(int iX=0; iX<Config_TofLoader::IMAGE_WIDTH; ++iX)
				GetData(iZ,iX,iY) = endian_swap(GetData(iZ,iX,iY));
#endif

	return iRet;
}


void TofImage::CheckArguments(int* piStartX, int* piEndX, int* piStartY, int* piEndY, int* piFolie, int* piZ)
{	
	if(piStartX && piEndX && piStartY && piEndY)
	{
		if(*piStartX>*piEndX) { int iTmp = *piStartX; *piStartX = *piEndX; *piEndX = iTmp; }
		if(*piStartY>*piEndY) { int iTmp = *piStartY; *piStartY = *piEndY; *piEndY = iTmp; }
		
		if(*piStartX<0) 
			*piStartX = 0;
		else if(*piStartX>Config_TofLoader::Config_TofLoader::IMAGE_WIDTH) 
			*piStartX = Config_TofLoader::Config_TofLoader::IMAGE_WIDTH;
		if(*piEndX<0) 
			*piEndX = 0;
		else if(*piEndX>Config_TofLoader::Config_TofLoader::IMAGE_WIDTH) 
			*piEndX = Config_TofLoader::Config_TofLoader::IMAGE_WIDTH;
		
		if(*piStartY<0) 
			*piStartY = 0;
		else if(*piStartY>Config_TofLoader::Config_TofLoader::IMAGE_HEIGHT) 
			*piStartY = Config_TofLoader::Config_TofLoader::IMAGE_HEIGHT;
		if(*piEndY<0) 
			*piEndY = 0;
		else if(*piEndY>Config_TofLoader::Config_TofLoader::IMAGE_HEIGHT) 
			*piEndY = Config_TofLoader::Config_TofLoader::IMAGE_HEIGHT;
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

// GetROI
// pix start x, pix ende x, pix start y, pix end y, folie (n=0..3; 0=0.., 1=32.., 2=128, 3=160), wievielte tof-image dieser folie (0..15), wenn 0, dann 16 auch dazuzählen
void TofImage::GetROI(int iStartX, int iEndX, int iStartY, int iEndY, int iFolie, int iTimechannel, TmpImage *pImg)
{
	CheckArguments(&iStartX, &iEndX, &iStartY, &iEndY, &iFolie, &iTimechannel);

	const int iBildBreite = iEndX-iStartX;
	const int iBildHoehe = iEndY-iStartY;
	unsigned int *puiWave = CreateUIntWave("wave",iBildBreite,iBildHoehe);
	if(puiWave==NULL) return;
	
	if(pImg!=NULL)
	{
		pImg->Clear();
		pImg->m_iW = iBildBreite;
		pImg->m_iH = iBildHoehe;
		pImg->m_puiDaten = puiWave;
	}

	for(int iY=iStartY; iY<iEndY; ++iY)
		for(int iX=iStartX; iX<iEndX; ++iX)
			puiWave[(iX-iStartX) + (iY-iStartY)*iBildBreite] = GetData(iFolie,iTimechannel,iX,iY);
}

// TOF-Graph
// pix start x, pix ende x, pix start y, pix end y, folie (n=0..3; 0=0.., 1=32.., 2=128, 3=160)
// alle Pixel eines Kanals addieren
void TofImage::GetGraph(int iStartX, int iEndX, int iStartY, int iEndY, int iFolie, TmpGraph* pGraph)
{
	CheckArguments(&iStartX, &iEndX, &iStartY, &iEndY, &iFolie);
	
	unsigned int *puiWave = CreateUIntWave("wave",Config_TofLoader::IMAGES_PER_FOIL,0);
	if(puiWave==NULL) return;
	
	if(pGraph!=NULL)
	{
		pGraph->m_iW = Config_TofLoader::IMAGES_PER_FOIL;
		pGraph->m_puiDaten = puiWave;
	}

	for(int iZ0=0; iZ0<Config_TofLoader::IMAGES_PER_FOIL; ++iZ0)
	{
		unsigned int uiSummedVal=0;
		for(int iY=iStartY; iY<iEndY; ++iY)
			for(int iX=iStartX; iX<iEndX; ++iX)
				uiSummedVal += GetData(iFolie, iZ0, iX, iY);
			
		puiWave[iZ0]=uiSummedVal;
	}
}

void TofImage::GetTotalGraph(int iStartX, int iEndX, int iStartY, int iEndY, double dPhaseShift, TmpGraph* pGraph)
{
	CheckArguments(&iStartX, &iEndX, &iStartY, &iEndY);
	
	unsigned int *puiWave = CreateUIntWave("wave",Config_TofLoader::IMAGES_PER_FOIL,0);
	if(puiWave==NULL) return;
	
	if(pGraph!=NULL)
	{
		pGraph->m_iW = Config_TofLoader::IMAGES_PER_FOIL;
		pGraph->m_puiDaten = puiWave;
	}

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
void TofImage::GetOverview(TmpImage *pImg)
{
	pImg->Clear();
	pImg->m_iW = Config_TofLoader::IMAGE_WIDTH;
	pImg->m_iH = Config_TofLoader::IMAGE_HEIGHT;
	pImg->m_puiDaten = CreateUIntWave("",Config_TofLoader::IMAGE_WIDTH,Config_TofLoader::IMAGE_HEIGHT);
	if(pImg->m_puiDaten==NULL) return;
	memset(pImg->m_puiDaten,0,sizeof(int)*pImg->m_iW*pImg->m_iH);
	
	for(int iFolie=0; iFolie<Config_TofLoader::FOIL_COUNT; ++iFolie)
		for(int iZ0=0; iZ0<Config_TofLoader::IMAGES_PER_FOIL; ++iZ0)
			for(int iY=0; iY<Config_TofLoader::IMAGE_HEIGHT; ++iY)
				for(int iX=0; iX<Config_TofLoader::IMAGE_WIDTH; ++iX)
					pImg->m_puiDaten[iY*Config_TofLoader::IMAGE_WIDTH+iX] += GetData(iFolie,iZ0,iX,iY);
}

// Alle Folien, die in iBits als aktiv markiert sind, addieren;
// dasselbe fuer die Kanaele
void TofImage::AddFoils(int iBits, int iZeitKanaeleBits, TmpImage *pImg)
{
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
	
	unsigned int uiAusgabe[Config_TofLoader::IMAGE_HEIGHT][Config_TofLoader::IMAGE_WIDTH];
	memset(uiAusgabe,0,Config_TofLoader::IMAGE_HEIGHT*Config_TofLoader::IMAGE_WIDTH*sizeof(int));
	
	unsigned int *puiWave = CreateUIntWave("wave",Config_TofLoader::IMAGE_WIDTH,Config_TofLoader::IMAGE_HEIGHT);
	if(puiWave==NULL) return;
	
	if(pImg!=NULL)
	{
		pImg->Clear();
		pImg->m_iW = Config_TofLoader::IMAGE_WIDTH;
		pImg->m_iH = Config_TofLoader::IMAGE_HEIGHT;
		pImg->m_puiDaten = puiWave;
	}

	for(int iFolie=0; iFolie<Config_TofLoader::FOIL_COUNT; ++iFolie)
	{
		if(!bFolieAktiv[iFolie]) continue;

		for(int iZ0=0; iZ0<Config_TofLoader::IMAGES_PER_FOIL; ++iZ0)
		{
			if (!bKanaeleAktiv[iZ0]) continue;
			for(int iY=0; iY<Config_TofLoader::IMAGE_HEIGHT; ++iY)
				for(int iX=0; iX<Config_TofLoader::IMAGE_WIDTH; ++iX)
					uiAusgabe[iY][iX] += GetData(iFolie,iZ0,iX,iY);
		}
	}
	
	for(int iY=0; iY<Config_TofLoader::IMAGE_HEIGHT; ++iY)
		for(int iX=0; iX<Config_TofLoader::IMAGE_WIDTH; ++iX)
				puiWave[iY*Config_TofLoader::IMAGE_WIDTH+iX] = uiAusgabe[iY][iX];
}

// Alle Kanaele, die im bool-Feld gesetzt sind, addieren
void TofImage::AddFoils(const bool *pbKanaele, TmpImage *pImg)
{
	unsigned int uiAusgabe[Config_TofLoader::IMAGE_HEIGHT][Config_TofLoader::IMAGE_WIDTH];
	memset(uiAusgabe,0,Config_TofLoader::IMAGE_HEIGHT*Config_TofLoader::IMAGE_WIDTH*sizeof(int));
	
	unsigned int *puiWave = CreateUIntWave("wave",Config_TofLoader::IMAGE_WIDTH,Config_TofLoader::IMAGE_HEIGHT);
	if(puiWave==NULL) return;
	
	if(pImg!=NULL)
	{
		pImg->Clear();
		pImg->m_iW = Config_TofLoader::IMAGE_WIDTH;
		pImg->m_iH = Config_TofLoader::IMAGE_HEIGHT;
		pImg->m_puiDaten = puiWave;
	}

	for(int iFolie=0; iFolie<Config_TofLoader::FOIL_COUNT; ++iFolie)
	{
		for(int iZ0=0; iZ0<Config_TofLoader::IMAGES_PER_FOIL; ++iZ0)
		{
			if(!pbKanaele[iFolie*Config_TofLoader::IMAGES_PER_FOIL + iZ0]) continue;
			
			for(int iY=0; iY<Config_TofLoader::IMAGE_HEIGHT; ++iY)
				for(int iX=0; iX<Config_TofLoader::IMAGE_WIDTH; ++iX)
					uiAusgabe[iY][iX] += GetData(iFolie, iZ0, iX, iY);
		}
	}
	
	for(int iY=0; iY<Config_TofLoader::IMAGE_HEIGHT; ++iY)
		for(int iX=0; iX<Config_TofLoader::IMAGE_WIDTH; ++iX)
				puiWave[iY*Config_TofLoader::IMAGE_WIDTH+iX] = uiAusgabe[iY][iX];
}

// Alle Phasenbilder, die im bool-Feld gesetzt sind, addieren
void TofImage::AddPhases(const bool *pbFolien, TmpImage *pImg)
{
	if(pImg==NULL) return;
	double *pdWave = CreateDoubleWave(NULL,Config_TofLoader::IMAGE_WIDTH,Config_TofLoader::IMAGE_HEIGHT);
	if(pdWave==NULL) return;

	pImg->Clear();
	pImg->m_iW = Config_TofLoader::IMAGE_WIDTH;
	pImg->m_iH = Config_TofLoader::IMAGE_HEIGHT;
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
void TofImage::AddContrasts(const bool *pbFolien, TmpImage *pImg)
{
	if(pImg==NULL) return;
	double *pdWave = CreateDoubleWave(NULL,Config_TofLoader::IMAGE_WIDTH,Config_TofLoader::IMAGE_HEIGHT);
	if(pdWave==NULL) return;

	pImg->Clear();
	pImg->m_iW = Config_TofLoader::IMAGE_WIDTH;
	pImg->m_iH = Config_TofLoader::IMAGE_HEIGHT;
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
void TofImage::GetPhaseGraph(int iFoil, TmpImage *pImg, bool bInDeg)
{
	GetPhaseGraph(iFoil, pImg, 0, Config_TofLoader::IMAGE_WIDTH, 0, Config_TofLoader::IMAGE_HEIGHT, bInDeg);
}

void TofImage::GetPhaseGraph(int iFolie, TmpImage *pImg, int iStartX, int iEndX, int iStartY, int iEndY, bool bInDeg)
{
	if(pImg==NULL) return;
	CheckArguments(&iStartX, &iEndX, &iStartY, &iEndY);

	pImg->Clear();
	pImg->m_iW = iEndX-iStartX;
	pImg->m_iH = iEndY-iStartY;
	
	const int XSIZE = Config_TofLoader::iPhaseBlockSize[0],
		  YSIZE = Config_TofLoader::iPhaseBlockSize[1];	
	
	double *pdWave = CreateDoubleWave(NULL,pImg->m_iW+XSIZE,pImg->m_iH+YSIZE);
	if(pdWave==NULL) return;
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

void TofImage::GetContrastGraph(int iFoil, TmpImage *pImg)
{
	GetContrastGraph(iFoil, pImg, 0, Config_TofLoader::IMAGE_WIDTH, 0, Config_TofLoader::IMAGE_HEIGHT);
}

void TofImage::GetContrastGraph(int iFoil, TmpImage *pImg, int iStartX, int iEndX, int iStartY, int iEndY)
{
	if(pImg==NULL) return;
	CheckArguments(&iStartX, &iEndX, &iStartY, &iEndY);

	pImg->Clear();
	pImg->m_iW = iEndX-iStartX;
	pImg->m_iH = iEndY-iStartY;
	
	const int XSIZE = Config_TofLoader::iContrastBlockSize[0],
		  YSIZE = Config_TofLoader::iContrastBlockSize[1];	
	
	double *pdWave = CreateDoubleWave(NULL,pImg->m_iW+XSIZE,pImg->m_iH+YSIZE);
	if(pdWave==NULL) return;
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

/////////////////////////////////////////

TmpImage TofImage::GetROI(int iStartX, int iEndX, int iStartY, int iEndY, int iFolie, int iZ)
{
	TmpImage img;
	GetROI(iStartX, iEndX, iStartY, iEndY, iFolie, iZ, &img);
	return img;
}

TmpGraph TofImage::GetGraph(int iStartX, int iEndX, int iStartY, int iEndY, int iFolie)
{
	TmpGraph graph;
	GetGraph(iStartX, iEndX, iStartY, iEndY, iFolie, &graph);
	return graph;
}

TmpGraph TofImage::GetTotalGraph(int iStartX, int iEndX, int iStartY, int iEndY, double dPhaseShift)
{
	TmpGraph graph;
	GetTotalGraph(iStartX, iEndX, iStartY, iEndY, dPhaseShift, &graph);
	return graph;
}

TmpImage TofImage::GetOverview()
{
	TmpImage img;
	GetOverview(&img);
	return img;
}

TmpImage TofImage::GetPhaseGraph(int iFolie, int iStartX, int iEndX, int iStartY, int iEndY, bool bInDeg)
{
	TmpImage img;
	GetPhaseGraph(iFolie, &img, iStartX, iEndX, iStartY, iEndY, bInDeg);
	return img;
}

TmpImage TofImage::GetContrastGraph(int iFolie, int iStartX, int iEndX, int iStartY, int iEndY)
{
	TmpImage img;
	GetContrastGraph(iFolie, &img, iStartX, iEndX, iStartY, iEndY);
	return img;
}

TmpImage TofImage::AddFoils(const bool *pbKanaele)
{
	TmpImage img;
	AddFoils(pbKanaele, &img);
	return img;
}

TmpImage TofImage::AddPhases(const bool *pbFolien)
{
	TmpImage img;
	AddPhases(pbFolien, &img);
	return img;
}

TmpImage TofImage::AddContrasts(const bool *pbFolien)
{
	TmpImage img;
	AddContrasts(pbFolien, &img);
	return img;
}

////////////////// TOF //////////////////



////////////////// PAD //////////////////
PadImage::PadImage(const char *pcFileName) : m_iMin(0),m_iMax(0)
{
	m_puiDaten = new unsigned int[Config_TofLoader::IMAGE_WIDTH*Config_TofLoader::IMAGE_HEIGHT];
	
	if(pcFileName!=NULL)
		LoadFile(pcFileName);
	else 
		memset(m_puiDaten,0,Config_TofLoader::IMAGE_HEIGHT*Config_TofLoader::IMAGE_WIDTH*sizeof(int));
}

PadImage::PadImage(const PadImage& pad)
{
	m_iMin=pad.m_iMin; 
	m_iMax=pad.m_iMax;
	
	m_puiDaten = new unsigned int[Config_TofLoader::IMAGE_WIDTH*Config_TofLoader::IMAGE_HEIGHT];
	memcpy(m_puiDaten, pad.m_puiDaten, sizeof(int)*Config_TofLoader::IMAGE_HEIGHT*Config_TofLoader::IMAGE_WIDTH);
}

void PadImage::Clear()
{
	if(m_puiDaten) { delete[] m_puiDaten; m_puiDaten=0; }
}

PadImage::~PadImage()
{
	Clear();
}

void PadImage::UpdateRange()
{
	m_iMin=std::numeric_limits<double>::max();
	m_iMax=0;
	for(int iY=0; iY<Config_TofLoader::IMAGE_HEIGHT; ++iY)
	{
		for(int iX=0; iX<Config_TofLoader::IMAGE_WIDTH; ++iX)
		{
			m_iMin = (m_iMin<int(GetData(iX,iY)))?m_iMin:GetData(iX,iY);
			m_iMax = (m_iMax>int(GetData(iX,iY)))?m_iMax:GetData(iX,iY);
		}
	}
}

int PadImage::LoadMem(const unsigned int *puiBuf, unsigned int uiBufLen)
{
	if(uiBufLen!=(unsigned int)Config_TofLoader::IMAGE_HEIGHT*Config_TofLoader::IMAGE_WIDTH)
	{
		std::cerr << "Error: Buffer size (" << uiBufLen << " ints) != PAD size (" << Config_TofLoader::IMAGE_HEIGHT*Config_TofLoader::IMAGE_WIDTH << " ints)." << std::endl;
		return LOAD_SIZE_MISMATCH;
	}
	
	memcpy(m_puiDaten, puiBuf, sizeof(int)*Config_TofLoader::IMAGE_HEIGHT*Config_TofLoader::IMAGE_WIDTH);
	
	// falls PowerPC, ints von little zu big endian konvertieren
#ifdef __BIG_ENDIAN__
		for(int iY=0; iY<Config_TofLoader::IMAGE_HEIGHT; ++iY)
			for(int iX=0; iX<Config_TofLoader::IMAGE_WIDTH; ++iX)
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
		std::cerr << "Error: Could not open file \"" << pcFileName << "\"." << std::endl;
		return LOAD_FAIL;
	}
	
	unsigned int uiBufLen = fread(m_puiDaten, sizeof(unsigned int),Config_TofLoader::IMAGE_HEIGHT*Config_TofLoader::IMAGE_WIDTH,pf);
	if(!uiBufLen)
	{
		std::cerr << "Error: Could not read file \"" << pcFileName << "\"." << std::endl;
	}
	
	if(uiBufLen!=(unsigned int)Config_TofLoader::IMAGE_HEIGHT*Config_TofLoader::IMAGE_WIDTH)
	{
		std::cerr << "Error: Buffer size (" << uiBufLen << " ints) != PAD size (" << Config_TofLoader::IMAGE_HEIGHT*Config_TofLoader::IMAGE_WIDTH << " ints)." << std::endl;
		iRet = LOAD_SIZE_MISMATCH;
	}	
	fclose(pf);
	
// falls PowerPC, ints von little zu big endian konvertieren
#ifdef __BIG_ENDIAN__
	for(int iY=0; iY<Config_TofLoader::IMAGE_HEIGHT; ++iY)
		for(int iX=0; iX<Config_TofLoader::IMAGE_WIDTH; ++iX)
			GetData(iX,iY) = endian_swap(GetData(iX,iY));
#endif	

	UpdateRange();
	return iRet;
}


#ifdef IGOR_PLUGIN
void PadImage::Print(const char* pcBaseName)
{
	unsigned int *pData = CreateUIntWave(pcBaseName,Config_TofLoader::IMAGE_WIDTH,Config_TofLoader::IMAGE_HEIGHT);
	if(pData==NULL)
	{
		XOPNotice("Konnte Wave nicht erstellen.");
		return;
	}

	for(int iY=0; iY<Config_TofLoader::IMAGE_HEIGHT; ++iY)
		for(int iX=0; iX<Config_TofLoader::IMAGE_WIDTH; ++iX)
			pData[iX+iY*Config_TofLoader::IMAGE_WIDTH] = GetData(iX,iY);
}
#else
void PadImage::Print(const char* pcOutFile)
{
	std::ostream* fOut = &std::cout;
	if(pcOutFile!=NULL)
		fOut = new std::ofstream(pcOutFile);

	for(int iY=0; iY<Config_TofLoader::IMAGE_HEIGHT; ++iY)
	{
		for(int iX=0; iX<Config_TofLoader::IMAGE_WIDTH; ++iX)
				(*fOut) << GetData(iX,iY) << "\t";
		(*fOut) << "\n";
	}
	
	(*fOut) << std::endl;
	if(pcOutFile!=NULL)
	{
		((std::ofstream*)fOut)->close();
		delete fOut;
	}	
}
#endif

unsigned int* PadImage::GetRawData(void)
{
	return m_puiDaten;
}

unsigned int PadImage::GetData(int iX, int iY) const
{
	if(m_puiDaten==NULL) return 0;
	
	if(iX>=0 && iX<Config_TofLoader::IMAGE_WIDTH && iY>=0 && iY<Config_TofLoader::IMAGE_HEIGHT)
		return m_puiDaten[iY*Config_TofLoader::IMAGE_WIDTH + iX];
	else 
		return 0;
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
		memcpy(m_puiDaten,tmp.m_puiDaten,sizeof(int)*m_iW*m_iH);
	}
	if(tmp.m_pdDaten)
	{
		m_pdDaten = new double[m_iW*m_iH];
		memcpy(m_pdDaten,tmp.m_pdDaten,sizeof(double)*m_iW*m_iH);
	}			
}
	
void TmpImage::Clear(void)
{
	if(m_puiDaten!=NULL)
	{
		delete[] m_puiDaten;
		m_puiDaten=NULL;
	}
	if(m_pdDaten!=NULL)
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
		{
			return double(m_puiDaten[iY*m_iW + iX]);
		}
		else if(m_pdDaten)
		{
			return m_pdDaten[iY*m_iW + iX];
		}
	}
	return 0.;
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

bool TmpImage::WriteXML(const char* pcFileName)
{
	std::ofstream ofstr(pcFileName);
	if(!ofstr.is_open()) return false;
	
	ofstr << "<measurement_file>\n";
	ofstr << "<instrument_name>MIRA</instrument_name>\n";
	ofstr << "<location>Forschungsreaktor Muenchen II - FRM2</location>\n";
	
	ofstr << "<measurement_data>\n";
	ofstr << "<resolution>1024</resolution>\n";
	ofstr << "<detector_value>\n";
	
	for(int iY=0; iY<m_iH; ++iY)
	{
		for (int t1=0; t1<8; ++t1) {
			for(int iX=0; iX<m_iW; ++iX)
			{
				for (int t2=0; t2<8; ++t2)
					ofstr << m_puiDaten[iX*m_iH + iY] << " ";
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
	m_iW = Config_TofLoader::IMAGE_WIDTH;
	m_iH = Config_TofLoader::IMAGE_HEIGHT;
	m_dMin = pPad->m_iMin;
	m_dMax = pPad->m_iMax;
	
	m_puiDaten = new unsigned int[Config_TofLoader::IMAGE_WIDTH*Config_TofLoader::IMAGE_HEIGHT];
	memcpy(m_puiDaten, pPad->m_puiDaten, Config_TofLoader::IMAGE_WIDTH*Config_TofLoader::IMAGE_HEIGHT*sizeof(int));
}


//////////////////////// TmpGraph ////////////////////////////

TmpGraph::TmpGraph()
{
	m_iW=0;
	m_puiDaten = NULL;
}

TmpGraph::~TmpGraph()
{
	if(m_puiDaten!=NULL)
	{
		delete m_puiDaten;
		m_puiDaten=NULL;
	}
}

unsigned int TmpGraph::GetData(int iX)
{
	if(!m_puiDaten) return 0;
	
	if(iX>=0 && iX<m_iW)
		return m_puiDaten[iX];
	return 0;
}

int TmpGraph::GetWidth(void) { return m_iW; }

int TmpGraph::GetMin()
{
	if(!m_puiDaten) return 0;
	
	unsigned int uiMin = std::numeric_limits<int>::max();
	for(int i=0; i<m_iW; ++i)
		if(m_puiDaten[i]<uiMin) uiMin = m_puiDaten[i];
	return uiMin;
}

int TmpGraph::GetMax()
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
				dchi2 += (m_pdy[i] - (damp*sin(double(i)*dscale + dphase)+doffs)) * (m_pdy[i] - (damp*sin(double(i)*dscale + dphase)+doffs)) / (dAbweichung*dAbweichung);
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

bool TmpGraph::FitSinus(double &dPhase, double &dScale, double &dAmp, double &dOffs)
{
	dScale = 2.*M_PI/double(Config_TofLoader::IMAGES_PER_FOIL); 	// Scale-Parameter fix
	
	double dMaxVal=GetMax(), dMinVal=GetMin();
	dOffs = dMinVal + (dMaxVal-dMinVal)/2.;		// Hint-Werte
	dAmp = (dMaxVal-dMinVal)/2.;			// Hint-Werte
	
	Sinus fkt;
	fkt.SetValues(m_iW,m_puiDaten);
	
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

	if(!mini.IsValid() /*|| dPhase!=dPhase || dAmp!=dAmp || dOffs!=dOffs*/)	// auf NaN prüfen
	{
		std::cerr << "Error: Invalid fit." << std::endl;	
		return false;
	}
	return true;
}
// ***************************************************************************
#else
bool TmpGraph::FitSinus(double &dPhase, double &dScale, double &dAmp, double &dOffs)
{
	std::cerr << "Error: Minuit not available." << std::endl;
	return false;
}
#endif
