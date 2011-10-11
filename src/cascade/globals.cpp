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

#include "globals.h"
#include "logger.h"
#include "helper.h"
#include "config.h"

#include <string.h>
#include <stdio.h>

// ************************* Configuration *************************************
// Default Values
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

// Defaults used in ROOT::Minuit2::MnApplication::operator()
double Config_TofLoader::dMinuitTolerance = 0.1;
unsigned int Config_TofLoader::uiMinuitMaxFcn = 0;
int Config_TofLoader::iMinuitAlgo = MINUIT_MIGRAD;
unsigned int Config_TofLoader::uiMinuitStrategy = 1;

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
	IMAGE_COUNT = Config::GetSingleton()->QueryInt(
				"/cascade_config/tof_file/image_count", IMAGE_COUNT);
	FOIL_COUNT = Config::GetSingleton()->QueryInt(
				"/cascade_config/tof_file/foil_count", FOIL_COUNT);
	IMAGES_PER_FOIL = Config::GetSingleton()->QueryInt(
				"/cascade_config/tof_file/images_per_foil", IMAGES_PER_FOIL);
	IMAGE_WIDTH = Config::GetSingleton()->QueryInt(
				"/cascade_config/tof_file/image_width", IMAGE_WIDTH);
	IMAGE_HEIGHT = Config::GetSingleton()->QueryInt(
				"/cascade_config/tof_file/image_height", IMAGE_HEIGHT);
	USE_PSEUDO_COMPRESSION = Config::GetSingleton()->QueryInt(
				"/cascade_config/tof_file/pseudo_compression",
				USE_PSEUDO_COMPRESSION);

	piFoilBegin = new int[FOIL_COUNT];
	for(int i=0; i<FOIL_COUNT; ++i)
	{
		char pcStr[256];
		sprintf(pcStr, "/cascade_config/tof_file/foil_%d_start", i+1);
		piFoilBegin[i] = Config::GetSingleton()->QueryInt(
				pcStr, IMAGES_PER_FOIL*2*i);
	}

	iPhaseBlockSize[0] = Config::GetSingleton()->QueryInt(
				"/cascade_config/graphs/phase_block_size_x",
				iPhaseBlockSize[0]);
	iPhaseBlockSize[1] = Config::GetSingleton()->QueryInt(
				"/cascade_config/graphs/phase_block_size_y",
				iPhaseBlockSize[1]);
	iContrastBlockSize[0] = Config::GetSingleton()->QueryInt(
				"/cascade_config/graphs/contrast_block_size_x",
				iContrastBlockSize[0]);
	iContrastBlockSize[1] = Config::GetSingleton()->QueryInt(
				"/cascade_config/graphs/contrast_block_size_y",
				iContrastBlockSize[1]);

	LOG_LOWER_RANGE = Config::GetSingleton()->QueryDouble(
				"/cascade_config/graphs/log_lower_range", LOG_LOWER_RANGE);

	dMinuitTolerance = Config::GetSingleton()->QueryDouble(
				"/cascade_config/minuit/tolerance", dMinuitTolerance);
	uiMinuitMaxFcn = (unsigned int)Config::GetSingleton()->QueryInt(
				"/cascade_config/minuit/maxfcn", uiMinuitMaxFcn);
	uiMinuitStrategy = (unsigned int)Config::GetSingleton()->QueryInt(
				"/cascade_config/minuit/strategy", uiMinuitStrategy);

	char pcAlgo[256];
	Config::GetSingleton()->QueryString(
				"/cascade_config/minuit/algo", pcAlgo, "migrad");
	if(strcasecmp(pcAlgo, "migrad")==0)
		iMinuitAlgo = MINUIT_MIGRAD;
	else if(strcasecmp(pcAlgo, "minimize")==0)
		iMinuitAlgo = MINUIT_MINIMIZE;
	else if(strcasecmp(pcAlgo, "simplex")==0)
		iMinuitAlgo = MINUIT_SIMPLEX;

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

// ***************************** Getter & Setter *******************************
double Config_TofLoader::GetLogLowerRange() { return LOG_LOWER_RANGE; }
int Config_TofLoader::GetFoilCount() { return FOIL_COUNT; }
int Config_TofLoader::GetImagesPerFoil() { return IMAGES_PER_FOIL; }
int Config_TofLoader::GetImageWidth() { return IMAGE_WIDTH; }
int Config_TofLoader::GetImageHeight() { return IMAGE_HEIGHT; }
int Config_TofLoader::GetImageCount() { return IMAGE_COUNT; }
bool Config_TofLoader::GetPseudoCompression() { return USE_PSEUDO_COMPRESSION; }
unsigned int Config_TofLoader::GetMinuitMaxFcn() { return uiMinuitMaxFcn; }
double Config_TofLoader::GetMinuitTolerance() { return dMinuitTolerance; }
int Config_TofLoader::GetMinuitAlgo() { return iMinuitAlgo; }
unsigned int Config_TofLoader::GetMinuitStrategy() { return uiMinuitStrategy; }

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

	// halbvernünftige Default-Werte setzen
	for(int i=0; i<iNumFoils; ++i)
		piFoilBegin[i] = GetNextPowerOfTwo(IMAGES_PER_FOIL)*i;
}

void Config_TofLoader::SetImagesPerFoil(int iNumImagesPerFoil)
{ IMAGES_PER_FOIL = iNumImagesPerFoil; }
void Config_TofLoader::SetImageWidth(int iImgWidth)
{ IMAGE_WIDTH = iImgWidth; }
void Config_TofLoader::SetImageHeight(int iImgHeight)
{ IMAGE_HEIGHT = iImgHeight; }
void Config_TofLoader::SetImageCount(int iImgCount)
{ IMAGE_COUNT = iImgCount; }
void Config_TofLoader::SetPseudoCompression(bool bSet)
{ USE_PSEUDO_COMPRESSION = bSet; }
void Config_TofLoader::SetMinuitMaxFnc(unsigned int uiMaxFcn)
{ uiMinuitMaxFcn = uiMaxFcn; }
void Config_TofLoader::SetMinuitTolerance(double dTolerance)
{ dMinuitTolerance = dTolerance; }
void Config_TofLoader::SetMinuitAlgo(int iAlgo)
{ iMinuitAlgo = iAlgo; }
void Config_TofLoader::SetMinuitStrategy(unsigned int uiStrategy)
{ uiMinuitStrategy = uiStrategy; }
void Config_TofLoader::SetLogLevel(int iLevel)
{ logger.SetLogLevel(iLevel); }
void Config_TofLoader::SetRepeatLogs(bool bRepeat)
{ logger.SetRepeatLogs(bRepeat); }

void Config_TofLoader::SetFoilBegin(int iFoil, int iOffs)
{
	if(iFoil<0 || iFoil>=FOIL_COUNT) return;

	piFoilBegin[iFoil] = iOffs;
}
// *****************************************************************************

void Config_TofLoader::CheckArguments(int* piStartX, int* piEndX, int* piStartY,
									  int* piEndY, int* piFolie, int* piZ)
{
	if(piStartX && piEndX && piStartY && piEndY)
	{
		if(*piStartX>*piEndX)
		{ int iTmp = *piStartX; *piStartX = *piEndX; *piEndX = iTmp; }
		if(*piStartY>*piEndY)
		{ int iTmp = *piStartY; *piStartY = *piEndY; *piEndY = iTmp; }

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

bool Config_TofLoader::GuessConfigFromSize(bool bPseudoCompressed, int iLen,
											bool bIsTof, bool bFirstCall)
{
	if(bFirstCall)
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "Loader: Trying to guess correct configuration."
			   " (Please configure the loader correctly using either"
			   " Config_TofLoader or the config file.)"
			   << "\n";
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
		for(unsigned int i=0; i<sizeof(iKnownCnt)/sizeof(int); ++i)
		{
			if(iKnownX[i]*iKnownY[i]*iKnownCnt[i] != iLen) continue;
			GuessConfigFromSize(bPseudoCompressed,iKnownX[i]*iKnownY[i],
								false,false);

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

				if(GuessConfigFromSize(bPseudoCompressed,iLen/iImgCnt,
										false, false))
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

				if(GuessConfigFromSize(bPseudoCompressed,iLen/iImgCnt,
										false, false))
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
		for(unsigned int i=0; i<sizeof(iKnownCnt)/sizeof(int); ++i)
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
// *****************************************************************************
