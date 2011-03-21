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
	#include "XOPStandardHeaders.h"
#endif

//////////////////////////// Konfiguration ///////////////////////////
// Default-Werte
int Config_TofLoader::FOLIENANZAHL = 4;
int Config_TofLoader::BILDERPROFOLIE = 16;
int Config_TofLoader::BILDBREITE = 64;
int Config_TofLoader::BILDHOEHE = 128;
int Config_TofLoader::BILDANZAHL = 196;
static const int g_iDefaultFolieBegin[] = {0, 32, 128, 160};
int *Config_TofLoader::piFolieBegin = 0 /*{0, 32, 128, 160}*/;

int Config_TofLoader::iPhaseBlockSize[2] = {1, 2};
int Config_TofLoader::iContrastBlockSize[2] = {1, 2};

double Config_TofLoader::LOG_LOWER_RANGE = -0.5;


void Config_TofLoader::Init()
{
	Deinit();

// Cascade-Qt-Client lädt Einstellungen über XML-Datei
#ifdef __CASCADE_QT_CLIENT__	
	BILDANZAHL = Config::GetSingleton()->QueryInt("/cascade_config/tof_file/image_count", BILDANZAHL);
	FOLIENANZAHL = Config::GetSingleton()->QueryInt("/cascade_config/tof_file/foil_count", FOLIENANZAHL);
	BILDERPROFOLIE = Config::GetSingleton()->QueryInt("/cascade_config/tof_file/images_per_foil", BILDERPROFOLIE);
	BILDBREITE = Config::GetSingleton()->QueryInt("/cascade_config/tof_file/image_width", BILDBREITE);
	BILDHOEHE = Config::GetSingleton()->QueryInt("/cascade_config/tof_file/image_height", BILDHOEHE);
	
	piFolieBegin = new int[FOLIENANZAHL];
	for(int i=0; i<FOLIENANZAHL; ++i)
	{
		char pcStr[256];
		sprintf(pcStr, "/cascade_config/tof_file/foil_%d_start", i+1);
		piFolieBegin[i] = Config::GetSingleton()->QueryInt(pcStr, g_iDefaultFolieBegin[i]);;
	}
	
	iPhaseBlockSize[0] = Config::GetSingleton()->QueryInt("/cascade_config/graphs/phase_block_size_x", iPhaseBlockSize[0]);
	iPhaseBlockSize[1] = Config::GetSingleton()->QueryInt("/cascade_config/graphs/phase_block_size_y", iPhaseBlockSize[1]);
	iContrastBlockSize[0] = Config::GetSingleton()->QueryInt("/cascade_config/graphs/contrast_block_size_x", iContrastBlockSize[0]);
	iContrastBlockSize[1] = Config::GetSingleton()->QueryInt("/cascade_config/graphs/contrast_block_size_y", iContrastBlockSize[1]);
	
	LOG_LOWER_RANGE = Config::GetSingleton()->QueryDouble("/cascade_config/graphs/log_lower_range", LOG_LOWER_RANGE);
	
#else	// Nicos-Client holt Einstellungen von Detektor

	// Defaults setzen
	piFolieBegin = new int[FOLIENANZAHL];
	for(int i=0; i<FOLIENANZAHL; ++i)
		piFolieBegin[i] = g_iDefaultFolieBegin[i];
	
	// TODO: richtige Einstellungen holen
#endif
}

void Config_TofLoader::Deinit()
{
	if(piFolieBegin)
	{
		delete[] piFolieBegin;
		piFolieBegin = 0;
	}
}

bool Config_TofLoader::GuessConfigFromSize(int iLen, bool bIsTof, bool bFirstCall)
{
	if(bFirstCall) std::cerr << "Warnung: Rate Konfiguration." << std::endl;

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
			BILDBREITE = iKnownX[i];
			BILDHOEHE = iKnownY[i];
			BILDANZAHL = iKnownCnt[i];
		}		
		
		if(!bFound)
		{
			// 2er-Potenzen absuchen
			for(int i=MIN_SHIFT; i<MAX_SHIFT; ++i)
			{
				int iImgCnt = 1<<i;
				if(iLen % iImgCnt) continue;
				
				if(GuessConfigFromSize(iLen/iImgCnt, false,false))
				{
					bFound = true;
					BILDANZAHL = iImgCnt;
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
					BILDANZAHL = iImgCnt;
					break;
				}
			}			
		}
		
		if(bFound)
		{
			std::cerr << "Bildanzahl: " << BILDANZAHL << std::endl;
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
			BILDBREITE = iKnownX[i];
			BILDHOEHE = iKnownY[i];
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
						BILDBREITE = iSideLenX;
						BILDHOEHE = iSideLenY;
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
						BILDBREITE = i;
						BILDHOEHE = j;
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
			std::cerr << "Bildbreite: " << BILDBREITE << std::endl;
			std::cerr << "Bildhöhe: " << BILDHOEHE << std::endl;
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
	if(m_puiDaten && iBild>=0 && iBild<Config_TofLoader::BILDANZAHL && iX>=0 && iX<Config_TofLoader::BILDBREITE && iY>=0 && iY<Config_TofLoader::BILDHOEHE)
		return m_puiDaten[iBild*Config_TofLoader::BILDBREITE*Config_TofLoader::BILDHOEHE + iY*Config_TofLoader::BILDBREITE + iX];
	return iDummy; // Referenz auf Dummy zurückgeben
}

unsigned int* TofImage::GetRawData(void) const
{
	return m_puiDaten;
}

TofImage::TofImage(const char *pcFileName)
{
	m_puiDaten = new unsigned int[Config_TofLoader::BILDANZAHL*Config_TofLoader::BILDHOEHE*Config_TofLoader::BILDBREITE];
	
	if(pcFileName!=NULL) LoadFile(pcFileName);
	else memset(m_puiDaten,0,Config_TofLoader::BILDANZAHL*Config_TofLoader::BILDHOEHE*Config_TofLoader::BILDBREITE*sizeof(int));
}

TofImage::~TofImage()
{
	Clear();
}

int TofImage::LoadMem(const unsigned int *puiBuf, unsigned int uiBufLen)
{
	if(uiBufLen!=(unsigned int)Config_TofLoader::BILDANZAHL*Config_TofLoader::BILDHOEHE*Config_TofLoader::BILDBREITE)
	{
		std::cerr << "Fehler: Puffergröße (" << uiBufLen << " ints) != TOF-Größe (" << Config_TofLoader::BILDANZAHL*Config_TofLoader::BILDHOEHE*Config_TofLoader::BILDBREITE << " ints)." << std::endl;
		return LOAD_SIZE_MISMATCH;
	}
	
	memcpy(m_puiDaten, puiBuf, sizeof(int)*Config_TofLoader::BILDANZAHL*Config_TofLoader::BILDHOEHE*Config_TofLoader::BILDBREITE);
	
// falls PowerPC, ints von little zu big endian konvertieren
#ifdef __BIG_ENDIAN__
	std::cerr << "Dies ist ein PowerPC (big endian)." << std::endl;
	for(int iZ=0; iZ<Config_TofLoader::BILDANZAHL; ++iZ)
		for(int iY=0; iY<Config_TofLoader::BILDHOEHE; ++iY)
			for(int iX=0; iX<Config_TofLoader::BILDBREITE; ++iX)
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
		std::cerr << "Konnte Datei \"" << pcFileName << "\" nicht oeffnen." << std::endl;
		return LOAD_FAIL;
	}
	
	unsigned int uiBufLen=fread(m_puiDaten, sizeof(unsigned int),Config_TofLoader::BILDANZAHL*Config_TofLoader::BILDHOEHE*Config_TofLoader::BILDBREITE,pf);
	if(!uiBufLen)
	{
		std::cerr << "Fehler beim Lesen der Datei \"" << pcFileName << "\"." << std::endl;
	}
	if(uiBufLen!=(unsigned int)Config_TofLoader::BILDANZAHL*Config_TofLoader::BILDHOEHE*Config_TofLoader::BILDBREITE)
	{
		std::cerr << "Fehler: Puffergröße (" << uiBufLen << " ints) != TOF-Größe (" << Config_TofLoader::BILDANZAHL*Config_TofLoader::BILDHOEHE*Config_TofLoader::BILDBREITE << " ints)." << std::endl;
		iRet = LOAD_SIZE_MISMATCH;
	}	
	
	fclose(pf);
	
// falls PowerPC, ints von little zu big endian konvertieren
#ifdef __BIG_ENDIAN__
	std::cerr << "Dies ist ein PowerPC (big endian)." << std::endl;
	for(int iZ=0; iZ<Config_TofLoader::BILDANZAHL; ++iZ)
		for(int iY=0; iY<Config_TofLoader::BILDHOEHE; ++iY)
			for(int iX=0; iX<Config_TofLoader::BILDBREITE; ++iX)
				GetData(iZ,iX,iY) = endian_swap(GetData(iZ,iX,iY));
#endif

	return iRet;
}


bool TofImage::CheckArguments(int iStartX, int iEndX, int iStartY, int iEndY, int iFolie, int iFolieInc)
{
	if(iStartX<0 || iStartX>=Config_TofLoader::BILDBREITE || iEndX<0 || iEndX>Config_TofLoader::BILDBREITE)
	{
		std::cerr << "Fehlerhaftes Argument! x=0.."<< Config_TofLoader::BILDBREITE-1 << std::endl;
		return false;
	}
	if(iStartY<0 || iStartY>=Config_TofLoader::BILDHOEHE || iEndY<0 || iEndY>Config_TofLoader::BILDHOEHE)
	{
		std::cerr << "Fehlerhaftes Argument! y=0.."<< Config_TofLoader::BILDHOEHE-1 << std::endl;
		return false;
	}
	if(iFolie<0 || iFolie>=Config_TofLoader::FOLIENANZAHL)
	{
		std::cerr << "Fehlerhaftes Argument! Folie=0.."<< Config_TofLoader::FOLIENANZAHL-1 << std::endl;
		return false;		
	}
	if(iFolieInc<0 || iFolieInc>=Config_TofLoader::BILDERPROFOLIE)
	{
		std::cerr << "Fehlerhaftes Argument! Zeitkanal=0.."<< Config_TofLoader::BILDERPROFOLIE-1 << std::endl;
		return false;		
	}
	return true;
}

// GetROI
// pix start x, pix ende x, pix start y, pix end y, folie (n=0..3; 0=0.., 1=32.., 2=128, 3=160), wievielste tof-image dieser folie (0..15), wenn 0, dann 16 auch dazuzählen
void TofImage::GetROI(int iStartX, int iEndX, int iStartY, int iEndY, int iFolie, int iFolieInc, const char* pcBaseName, TmpImage *pImg)
{
	if(iStartX>iEndX) { int iTmp = iStartX; iStartX = iEndX; iEndX = iTmp; }
	if(iStartY>iEndY) { int iTmp = iStartY; iStartY = iEndY; iEndY = iTmp; }

	if(!CheckArguments(iStartX, iEndX, iStartY, iEndY, iFolie, iFolieInc)) return;

	int iZ=0;
	switch(iFolie)
	{
		case 0: iZ=Config_TofLoader::piFolieBegin[0]; break;
		case 1: iZ=Config_TofLoader::piFolieBegin[1]; break;
		case 2: iZ=Config_TofLoader::piFolieBegin[2]; break;
		case 3: iZ=Config_TofLoader::piFolieBegin[3]; break;
	};
	
	const int iBildBreite = iEndX-iStartX;
	const int iBildHoehe = iEndY-iStartY;
	unsigned int *puiWave = CreateUIntWave(pcBaseName,iBildBreite,iBildHoehe);
	if(puiWave==NULL) return;
	
	if(pImg!=NULL)
	{
		pImg->Clear();
		pImg->m_iW = iBildBreite;
		pImg->m_iH = iBildHoehe;
		pImg->m_puiDaten = puiWave;
	}

	iZ += iFolieInc;		
	for(int iY=iStartY; iY<iEndY; ++iY)
	{
		for(int iX=iStartX; iX<iEndX; ++iX)
		{
			if(iFolieInc!=0)
				puiWave[(iX-iStartX) + (iY-iStartY)*iBildBreite] = GetData(iZ,iX,iY);
			else
				puiWave[(iX-iStartX) + (iY-iStartY)*iBildBreite] = GetData(iZ,iX,iY)+GetData(iZ+Config_TofLoader::BILDERPROFOLIE,iX,iY);
		}
	}
}

// TOF-Graph
// pix start x, pix ende x, pix start y, pix end y, folie (n=0..3; 0=0.., 1=32.., 2=128, 3=160)
// alle Pixel eines Kanals addieren
void TofImage::GetGraph(int iStartX, int iEndX, int iStartY, int iEndY, int iFolie, const char* pcBaseName, TmpGraph* pGraph)
{
	if(iStartX>iEndX) { int iTmp = iStartX; iStartX = iEndX; iEndX = iTmp; }
	if(iStartY>iEndY) { int iTmp = iStartY; iStartY = iEndY; iEndY = iTmp; }
	if(!CheckArguments(iStartX, iEndX, iStartY, iEndY, iFolie)) return;
	
	int iZ=0;
	switch(iFolie)
	{
		case 0: iZ=Config_TofLoader::piFolieBegin[0]; break;
		case 1: iZ=Config_TofLoader::piFolieBegin[1]; break;
		case 2: iZ=Config_TofLoader::piFolieBegin[2]; break;
		case 3: iZ=Config_TofLoader::piFolieBegin[3]; break;
	};
	
	unsigned int *puiWave = CreateUIntWave(pcBaseName,Config_TofLoader::BILDERPROFOLIE,0);
	if(puiWave==NULL) return;
	
	if(pGraph!=NULL)
	{
		pGraph->m_iW = Config_TofLoader::BILDERPROFOLIE;
		pGraph->m_puiDaten = puiWave;
	}

	int iCnt=0;
	for(int iZ0=0; iZ0<Config_TofLoader::BILDERPROFOLIE; ++iZ0)
	{
		unsigned int uiSummedVal=0;
		for(int iY=iStartY; iY<iEndY; ++iY)
		{
			for(int iX=iStartX; iX<iEndX; ++iX)
			{
				if(iZ0!=0)
					uiSummedVal += GetData(iZ+iZ0,iX,iY);
				else
					uiSummedVal += GetData(iZ+iZ0,iX,iY)+GetData(iZ+Config_TofLoader::BILDERPROFOLIE,iX,iY);
			}
		}
		puiWave[iCnt++]=uiSummedVal;
	}
}

void TofImage::GetTotalGraph(int iStartX, int iEndX, int iStartY, int iEndY, double dPhaseShift ,const char* pcBaseName, TmpGraph* pGraph)
{
	if(iStartX>iEndX) { int iTmp = iStartX; iStartX = iEndX; iEndX = iTmp; }
	if(iStartY>iEndY) { int iTmp = iStartY; iStartY = iEndY; iEndY = iTmp; }
	if(!CheckArguments(iStartX, iEndX, iStartY, iEndY)) return;
	
	unsigned int *puiWave = CreateUIntWave(pcBaseName,Config_TofLoader::BILDERPROFOLIE,0);
	if(puiWave==NULL) return;
	
	if(pGraph!=NULL)
	{
		pGraph->m_iW = Config_TofLoader::BILDERPROFOLIE;
		pGraph->m_puiDaten = puiWave;
	}

	int iCnt=0;
	// Zeitkanäle
	for(int iZ0=0; iZ0<Config_TofLoader::BILDERPROFOLIE; ++iZ0)
	{
		unsigned int uiSummedVal=0;
		for(int iY=iStartY; iY<iEndY; ++iY)
		{
			for(int iX=iStartX; iX<iEndX; ++iX)
			{
				// Folien
				for(int iFolie=0; iFolie<Config_TofLoader::FOLIENANZAHL; ++iFolie)
				{
					int iZ=Config_TofLoader::piFolieBegin[iFolie];
					int iShift = iZ0 + int(dPhaseShift*double(iFolie));
					if(iShift>=Config_TofLoader::BILDERPROFOLIE)
						iShift%=Config_TofLoader::BILDERPROFOLIE;
						
					if(iZ0!=0)
						uiSummedVal += GetData(iZ+iShift,iX,iY);
					else
						uiSummedVal += GetData(iZ+iShift,iX,iY)+GetData(iZ+Config_TofLoader::BILDERPROFOLIE,iX,iY);
				}
			}
		}
		puiWave[iCnt++]=uiSummedVal;
	}
}

// Summe aller Bilder
void TofImage::GetOverview(TmpImage *pImg)
{
	pImg->Clear();
	pImg->m_iW = Config_TofLoader::BILDBREITE;
	pImg->m_iH = Config_TofLoader::BILDHOEHE;
	pImg->m_puiDaten = CreateUIntWave("",Config_TofLoader::BILDBREITE,Config_TofLoader::BILDHOEHE);
	if(pImg->m_puiDaten==NULL) return;
	memset(pImg->m_puiDaten,0,sizeof(int)*pImg->m_iW*pImg->m_iH);
	
	for(int iFolie=0; iFolie<Config_TofLoader::FOLIENANZAHL; ++iFolie)
	{
		for(int iZ0=0; iZ0<Config_TofLoader::BILDERPROFOLIE; ++iZ0)
		{
			for(int iY=0; iY<Config_TofLoader::BILDHOEHE; ++iY)
				for(int iX=0; iX<Config_TofLoader::BILDBREITE; ++iX)
				{
					if(iZ0!=0)
						pImg->m_puiDaten[iY*Config_TofLoader::BILDBREITE+iX] += GetData(Config_TofLoader::piFolieBegin[iFolie]+iZ0,iX,iY);
					else
						pImg->m_puiDaten[iY*Config_TofLoader::BILDBREITE+iX] += GetData(Config_TofLoader::piFolieBegin[iFolie]+iZ0,iX,iY) + GetData(Config_TofLoader::piFolieBegin[iFolie]+Config_TofLoader::BILDERPROFOLIE,iX,iY);
				}
		}
	}
}

// Alle Folien, die in iBits als aktiv markiert sind, addieren;
// dasselbe fuer die Kanaele
void TofImage::AddFolien(int iBits, int iZeitKanaeleBits, const char* pcBaseName, TmpImage *pImg)
{
	bool bFolieAktiv[Config_TofLoader::FOLIENANZAHL],
		bKanaeleAktiv[Config_TofLoader::BILDERPROFOLIE];
	
	for(int i=0; i<Config_TofLoader::FOLIENANZAHL; ++i)
	{
		if(iBits & (1<<i)) bFolieAktiv[i]=true;
		else bFolieAktiv[i]=false;
	}
	
	for(int i=0; i<Config_TofLoader::BILDERPROFOLIE; ++i)
	{
		if(iZeitKanaeleBits & (1<<i)) bKanaeleAktiv[i]=true;
		else bKanaeleAktiv[i]=false;		
	}
	
	unsigned int uiAusgabe[Config_TofLoader::BILDHOEHE][Config_TofLoader::BILDBREITE];
	memset(uiAusgabe,0,Config_TofLoader::BILDHOEHE*Config_TofLoader::BILDBREITE*sizeof(int));
	
	unsigned int *puiWave = CreateUIntWave(pcBaseName,Config_TofLoader::BILDBREITE,Config_TofLoader::BILDHOEHE);
	if(puiWave==NULL) return;
	
	if(pImg!=NULL)
	{
		pImg->Clear();
		pImg->m_iW = Config_TofLoader::BILDBREITE;
		pImg->m_iH = Config_TofLoader::BILDHOEHE;
		pImg->m_puiDaten = puiWave;
	}

	for(int iFolie=0; iFolie<Config_TofLoader::FOLIENANZAHL; ++iFolie)
	{
		if(!bFolieAktiv[iFolie]) continue;
		
		for(int iZ0=0; iZ0<Config_TofLoader::BILDERPROFOLIE; ++iZ0)
		{
			if (!bKanaeleAktiv[iZ0]) continue;
			for(int iY=0; iY<Config_TofLoader::BILDHOEHE; ++iY)
				for(int iX=0; iX<Config_TofLoader::BILDBREITE; ++iX)
				{
					if(iZ0!=0)
						uiAusgabe[iY][iX] += GetData(Config_TofLoader::piFolieBegin[iFolie]+iZ0,iX,iY);
					else
						uiAusgabe[iY][iX] += GetData(Config_TofLoader::piFolieBegin[iFolie]+iZ0,iX,iY) + GetData(Config_TofLoader::piFolieBegin[iFolie]+Config_TofLoader::BILDERPROFOLIE,iX,iY);
				}
		}
	}
	
	for(int iY=0; iY<Config_TofLoader::BILDHOEHE; ++iY)
		for(int iX=0; iX<Config_TofLoader::BILDBREITE; ++iX)
				puiWave[iY*Config_TofLoader::BILDBREITE+iX] = uiAusgabe[iY][iX];
}

// Alle Kanaele, die im bool-Feld gesetzt sind, addieren
void TofImage::AddFolien(const bool *pbKanaele, const char* pcBaseName, TmpImage *pImg)
{
	unsigned int uiAusgabe[Config_TofLoader::BILDHOEHE][Config_TofLoader::BILDBREITE];
	memset(uiAusgabe,0,Config_TofLoader::BILDHOEHE*Config_TofLoader::BILDBREITE*sizeof(int));
	
	unsigned int *puiWave = CreateUIntWave(pcBaseName,Config_TofLoader::BILDBREITE,Config_TofLoader::BILDHOEHE);
	if(puiWave==NULL) return;
	
	if(pImg!=NULL)
	{
		pImg->Clear();
		pImg->m_iW = Config_TofLoader::BILDBREITE;
		pImg->m_iH = Config_TofLoader::BILDHOEHE;
		pImg->m_puiDaten = puiWave;
	}

	for(int iFolie=0; iFolie<Config_TofLoader::FOLIENANZAHL; ++iFolie)
	{
		for(int iZ0=0; iZ0<Config_TofLoader::BILDERPROFOLIE; ++iZ0)
		{
			if(!pbKanaele[iFolie*Config_TofLoader::BILDERPROFOLIE + iZ0]) continue;
			
			for(int iY=0; iY<Config_TofLoader::BILDHOEHE; ++iY)
				for(int iX=0; iX<Config_TofLoader::BILDBREITE; ++iX)
				{
					if(iZ0!=0)
						uiAusgabe[iY][iX] += GetData(Config_TofLoader::piFolieBegin[iFolie]+iZ0, iX, iY);
					else
						uiAusgabe[iY][iX] += GetData(Config_TofLoader::piFolieBegin[iFolie]+iZ0, iX, iY) + GetData(Config_TofLoader::piFolieBegin[iFolie]+Config_TofLoader::BILDERPROFOLIE, iX, iY);
				}
		}
	}
	
	for(int iY=0; iY<Config_TofLoader::BILDHOEHE; ++iY)
		for(int iX=0; iX<Config_TofLoader::BILDBREITE; ++iX)
				puiWave[iY*Config_TofLoader::BILDBREITE+iX] = uiAusgabe[iY][iX];
}

// Alle Phasenbilder, die im bool-Feld gesetzt sind, addieren
void TofImage::AddPhases(const bool *pbFolien, const char* pcBaseName, TmpImage *pImg)
{
	if(pImg==NULL) return;
	double *pdWave = CreateDoubleWave(NULL,Config_TofLoader::BILDBREITE,Config_TofLoader::BILDHOEHE);
	if(pdWave==NULL) return;

	pImg->Clear();
	pImg->m_iW = Config_TofLoader::BILDBREITE;
	pImg->m_iH = Config_TofLoader::BILDHOEHE;
	pImg->m_pdDaten = pdWave;
	
	memset(pdWave, 0, sizeof(double)*pImg->m_iW*pImg->m_iH);
	
	for(int iFolie=0; iFolie<Config_TofLoader::FOLIENANZAHL; ++iFolie)
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
void TofImage::AddContrasts(const bool *pbFolien, const char* pcBaseName, TmpImage *pImg)
{
	if(pImg==NULL) return;
	double *pdWave = CreateDoubleWave(NULL,Config_TofLoader::BILDBREITE,Config_TofLoader::BILDHOEHE);
	if(pdWave==NULL) return;

	pImg->Clear();
	pImg->m_iW = Config_TofLoader::BILDBREITE;
	pImg->m_iH = Config_TofLoader::BILDHOEHE;
	pImg->m_pdDaten = pdWave;
	
	memset(pdWave, 0, sizeof(double)*pImg->m_iW*pImg->m_iH);
	
	for(int iFolie=0; iFolie<Config_TofLoader::FOLIENANZAHL; ++iFolie)
	{
		if(!pbFolien[iFolie]) continue;
			
		TmpImage tmpimg;
		GetContrastGraph(iFolie, &tmpimg);
	
		pImg->Add(tmpimg);
	}
}

// Für Kalibrierungsdiagramm
void TofImage::GetPhaseGraph(int iFolie, TmpImage *pImg, int iStartX, int iEndX, int iStartY, int iEndY, bool bInDeg)
{
	if(iStartX<0 || iEndX<0 || iStartY<0 || iEndY<0)
	{
		iStartX = 0;
		iEndX = Config_TofLoader::Config_TofLoader::BILDBREITE;
		iStartY = 0;
		iEndY = Config_TofLoader::Config_TofLoader::BILDHOEHE;
	}
	
	if(iStartX>iEndX) { int iTmp = iStartX; iStartX = iEndX; iEndX = iTmp; }
	if(iStartY>iEndY) { int iTmp = iStartY; iStartY = iEndY; iEndY = iTmp; }
	if(!CheckArguments(iStartX, iEndX, iStartY, iEndY)) return;
	
	if(pImg==NULL) return;
	double *pdWave = CreateDoubleWave(NULL,Config_TofLoader::BILDBREITE,Config_TofLoader::BILDHOEHE);
	if(pdWave==NULL) return;
	
	pImg->Clear();
	pImg->m_iW = iEndX-iStartX;
	pImg->m_iH = iEndY-iStartY;
	pImg->m_pdDaten = pdWave;
		
	const int XSIZE = Config_TofLoader::iPhaseBlockSize[0],
		  YSIZE = Config_TofLoader::iPhaseBlockSize[1];
	for(int iY=iStartY; iY<iEndY; iY+=YSIZE)
		for(int iX=iStartX; iX<iEndX; iX+=XSIZE)
		{	
			TmpGraph tmpGraph;
			GetGraph(iX, iX+XSIZE, iY, iY+YSIZE, iFolie, NULL, &tmpGraph);
			
			double dPhase, dFreq, dAmp, dOffs;
			bool bFitValid = tmpGraph.FitSinus(dPhase, dFreq, dAmp, dOffs);
			
			if(!bFitValid || dPhase!=dPhase)
			{
				dPhase = 0.;
				//std::cerr << "Fit für Pixel x=" << iX << ", y=" << iY << ", Folie=" << iFolie << " ungültig." << std::endl;
			}
			
			if(bInDeg) dPhase = dPhase*180./M_PI;
			
			for(int i=0; i<YSIZE; ++i)
				for(int j=0; j<XSIZE; ++j)
					pdWave[(iY-iStartY+i)*pImg->m_iW+(iX-iStartX+j)] = dPhase;
		}
}

void TofImage::GetContrastGraph(int iFolie, TmpImage *pImg)
{
	if(pImg==NULL) return;
	double *pdWave = CreateDoubleWave(NULL,Config_TofLoader::BILDBREITE,Config_TofLoader::BILDHOEHE);
	if(pdWave==NULL) return;
	
	pImg->Clear();
	pImg->m_iW = Config_TofLoader::BILDBREITE;
	pImg->m_iH = Config_TofLoader::BILDHOEHE;
	pImg->m_pdDaten = pdWave;
		
	const int XSIZE = Config_TofLoader::iContrastBlockSize[0],
		  YSIZE = Config_TofLoader::iContrastBlockSize[1];
	for(int iY=0; iY<Config_TofLoader::BILDHOEHE; iY+=YSIZE)
		for(int iX=0; iX<Config_TofLoader::BILDBREITE; iX+=XSIZE)
		{	
			TmpGraph tmpGraph;
			GetGraph(iX, iX+XSIZE, iY, iY+YSIZE, iFolie, NULL, &tmpGraph);
			
			double dPhase, dFreq, dAmp, dOffs;
			bool bFitValid = tmpGraph.FitSinus(dPhase, dFreq, dAmp, dOffs);
			
			double dContrast = fabs(dAmp/dOffs);
			if(!bFitValid || dContrast!=dContrast)
			{
				dContrast = 0.;
				//std::cerr << "Fit für Pixel x=" << iX << ", y=" << iY << ", Folie=" << iFolie << " ungültig." << std::endl;
			}
			
			for(int i=0; i<YSIZE; ++i)
				for(int j=0; j<XSIZE; ++j)
					pdWave[(iY+i)*Config_TofLoader::BILDBREITE+(iX+j)] = dContrast;
		}
}
////////////////// TOF //////////////////



////////////////// PAD //////////////////
PadImage::PadImage(const char *pcFileName) : m_iMin(0),m_iMax(0)
{
	m_puiDaten = new unsigned int[Config_TofLoader::BILDBREITE*Config_TofLoader::BILDHOEHE];
	
	if(pcFileName!=NULL)
		LoadFile(pcFileName);
	else 
		memset(m_puiDaten,0,Config_TofLoader::BILDHOEHE*Config_TofLoader::BILDBREITE*sizeof(int));
}

PadImage::PadImage(const PadImage& pad)
{
	m_iMin=pad.m_iMin; 
	m_iMax=pad.m_iMax;
	
	m_puiDaten = new unsigned int[Config_TofLoader::BILDBREITE*Config_TofLoader::BILDHOEHE];
	memcpy(m_puiDaten, pad.m_puiDaten, sizeof(int)*Config_TofLoader::BILDHOEHE*Config_TofLoader::BILDBREITE);
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
	for(int iY=0; iY<Config_TofLoader::BILDHOEHE; ++iY)
	{
		for(int iX=0; iX<Config_TofLoader::BILDBREITE; ++iX)
		{
			m_iMin = (m_iMin<int(GetData(iX,iY)))?m_iMin:GetData(iX,iY);
			m_iMax = (m_iMax>int(GetData(iX,iY)))?m_iMax:GetData(iX,iY);
		}
	}
}

int PadImage::LoadMem(const unsigned int *puiBuf, unsigned int uiBufLen)
{
	if(uiBufLen!=(unsigned int)Config_TofLoader::BILDHOEHE*Config_TofLoader::BILDBREITE)
	{
		std::cerr << "Fehler: Puffergröße (" << uiBufLen << " ints) != PAD-Größe (" << Config_TofLoader::BILDHOEHE*Config_TofLoader::BILDBREITE << " ints)." << std::endl;
		return LOAD_SIZE_MISMATCH;
	}
	
	memcpy(m_puiDaten, puiBuf, sizeof(int)*Config_TofLoader::BILDHOEHE*Config_TofLoader::BILDBREITE);
	
	// falls PowerPC, ints von little zu big endian konvertieren
	#ifdef __BIG_ENDIAN__
		std::cerr << "Dies ist ein PowerPC (big endian)." << std::endl;
		for(int iY=0; iY<Config_TofLoader::BILDHOEHE; ++iY)
			for(int iX=0; iX<Config_TofLoader::BILDBREITE; ++iX)
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
		std::cerr << "Konnte Datei \"" << pcFileName << "\" nicht oeffnen." << std::endl;
		return LOAD_FAIL;
	}
	
	unsigned int uiBufLen=uiBufLen=fread(m_puiDaten, sizeof(unsigned int),Config_TofLoader::BILDHOEHE*Config_TofLoader::BILDBREITE,pf);
	if(!uiBufLen)
	{
		std::cerr << "Fehler beim Lesen der Datei \"" << pcFileName << "\"." << std::endl;
	}
	
	if(uiBufLen!=(unsigned int)Config_TofLoader::BILDHOEHE*Config_TofLoader::BILDBREITE)
	{
		std::cerr << "Fehler: Puffergröße (" << uiBufLen << " ints) != PAD-Größe (" << Config_TofLoader::BILDHOEHE*Config_TofLoader::BILDBREITE << " ints)." << std::endl;
		iRet = LOAD_SIZE_MISMATCH;
	}	
	fclose(pf);
	
// falls PowerPC, ints von little zu big endian konvertieren
#ifdef __BIG_ENDIAN__
	std::cerr << "Dies ist ein PowerPC (big endian)." << std::endl;
	for(int iY=0; iY<Config_TofLoader::BILDHOEHE; ++iY)
		for(int iX=0; iX<Config_TofLoader::BILDBREITE; ++iX)
			GetData(iX,iY) = endian_swap(GetData(iX,iY));
#endif	

	UpdateRange();
	return iRet;
}


#ifdef IGOR_PLUGIN
void PadImage::Print(const char* pcBaseName)
{
	unsigned int *pData = CreateUIntWave(pcBaseName,Config_TofLoader::BILDBREITE,Config_TofLoader::BILDHOEHE);
	if(pData==NULL)
	{
		XOPNotice("Konnte Wave nicht erstellen.");
		return;
	}

	for(int iY=0; iY<Config_TofLoader::BILDHOEHE; ++iY)
		for(int iX=0; iX<Config_TofLoader::BILDBREITE; ++iX)
			pData[iX+iY*Config_TofLoader::BILDBREITE] = GetData(iX,iY);
}
#else
void PadImage::Print(const char* pcOutFile)
{
	std::ostream* fOut = &std::cout;
	if(pcOutFile!=NULL)
		fOut = new std::ofstream(pcOutFile);

	for(int iY=0; iY<Config_TofLoader::BILDHOEHE; ++iY)
	{
		for(int iX=0; iX<Config_TofLoader::BILDBREITE; ++iX)
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
	
	if(iX>=0 && iX<Config_TofLoader::BILDBREITE && iY>=0 && iY<Config_TofLoader::BILDHOEHE)
		return m_puiDaten[iY*Config_TofLoader::BILDBREITE + iX];
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
	ofstr << "<resolution> " << m_iW << "x" << m_iH << " </resolution>\n";
	ofstr << "<detector_value>\n";
	
	for(int iY=0; iY<m_iH; ++iY)
	{
		for(int iX=0; iX<m_iW; ++iX)
		{
			ofstr << m_puiDaten[iY*m_iW + iX] << " ";
		}
		ofstr << "\n";
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
	m_iW = Config_TofLoader::BILDBREITE;
	m_iH = Config_TofLoader::BILDHOEHE;
	m_dMin = pPad->m_iMin;
	m_dMax = pPad->m_iMax;
	
	m_puiDaten = new unsigned int[Config_TofLoader::BILDBREITE*Config_TofLoader::BILDHOEHE];
	memcpy(m_puiDaten, pPad->m_puiDaten, Config_TofLoader::BILDBREITE*Config_TofLoader::BILDHOEHE*sizeof(int));
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
			double dscale = /*params[3]*/ 2.*M_PI/double(Config_TofLoader::BILDERPROFOLIE);	// fest
			
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
	dScale = 2.*M_PI/double(Config_TofLoader::BILDERPROFOLIE); 	// Scale-Parameter fix
	
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
		std::cerr << "Fehler: Kein gültiger Fit!" << std::endl;	
		return false;
	}
	return true;
}
// ***************************************************************************
#else
bool TmpGraph::FitSinus(double &dPhase, double &dScale, double &dAmp, double &dOffs)
{
	std::cerr << "Fehler: Minuit nicht verfügbar." << std::endl;
	return false;
}
#endif
