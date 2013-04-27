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

#include "../config/globals.h"
#include "../config/config.h"
#include "../auxiliary/logger.h"
#include "../auxiliary/helper.h"

#include <string.h>
#include <stdio.h>
#include <iostream>
#include <time.h>
#include <math.h>

//------------------------------------------------------------------------------
// PAD config

PadConfig::PadConfig()
{
	IMAGE_WIDTH = 128;
	IMAGE_HEIGHT = 128;
}

PadConfig::PadConfig(const PadConfig& conf)
{
	(*this) = conf;
}

const PadConfig& PadConfig::operator=(const PadConfig& conf)
{
	IMAGE_WIDTH = conf.IMAGE_WIDTH;
	IMAGE_HEIGHT = conf.IMAGE_HEIGHT;

	return *this;
}


int PadConfig::GetImageWidth() const { return IMAGE_WIDTH; }
int PadConfig::GetImageHeight() const { return IMAGE_HEIGHT; }

void PadConfig::SetImageWidth(int iImgWidth) { IMAGE_WIDTH = iImgWidth; }
void PadConfig::SetImageHeight(int iImgHeight) { IMAGE_HEIGHT = iImgHeight; }

//------------------------------------------------------------------------------
// TOF config

TofConfig::TofConfig() : PadConfig()
{
	// defaults
	SetFoilCount(6);

	IMAGES_PER_FOIL = 16;
	IMAGE_COUNT = 128;

	USE_PSEUDO_COMPRESSION = 0;
	SUM_FIRST_AND_LAST = 0;
	NUM_OSC = 2.;
}

TofConfig::TofConfig(const TofConfig& conf) : PadConfig(conf)
{
	(*this) = conf;
}

const TofConfig& TofConfig::operator=(const TofConfig& conf)
{
	PadConfig::operator =(conf);

	FOIL_COUNT = conf.FOIL_COUNT;
	vecFoilBegin = conf.vecFoilBegin;

	IMAGES_PER_FOIL = conf.IMAGES_PER_FOIL;
	IMAGE_COUNT = conf.IMAGE_COUNT;

	USE_PSEUDO_COMPRESSION = conf.USE_PSEUDO_COMPRESSION;
	SUM_FIRST_AND_LAST = conf.SUM_FIRST_AND_LAST;
	NUM_OSC = conf.NUM_OSC;

	return *this;
}

void TofConfig::CheckNumOscillations()
{
	if(NUM_OSC < 0.)
		NUM_OSC = -NUM_OSC;

	double dNumOscInt = floor(NUM_OSC);
	if(!float_equal<double>(NUM_OSC, dNumOscInt))
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "Globals: Number of oscillations have to be integer for "
				 "fourier calculations to work.\n";
	}
}

int TofConfig::GetFoilCount() const { return FOIL_COUNT; }
int TofConfig::GetImagesPerFoil() const { return IMAGES_PER_FOIL; }
int TofConfig::GetImageCount() const { return IMAGE_COUNT; }
bool TofConfig::GetPseudoCompression() const { return USE_PSEUDO_COMPRESSION; }
bool TofConfig::GetSumFirstAndLast() const { return SUM_FIRST_AND_LAST; }
double TofConfig::GetNumOscillations() const { return NUM_OSC; }

int TofConfig::GetFoilBegin(int iFoil) const
{
	if(iFoil<0 || iFoil>=FOIL_COUNT) return -1;
	return vecFoilBegin[iFoil];
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

void TofConfig::SetFoilCount(int iNumFoils)
{
	FOIL_COUNT = iNumFoils;
	vecFoilBegin.resize(iNumFoils);

	const int iBegins[] = {0, 16, 32, 64, 80, 96};

	for(int i=0; i<iNumFoils; ++i)
	{
		if(i < sizeof(iBegins)/sizeof(int))
			vecFoilBegin[i] = iBegins[i];
		else
			vecFoilBegin[i] = GetNextPowerOfTwo(IMAGES_PER_FOIL)*i;
	}
}

void TofConfig::SetFoilBegin(int iFoil, int iOffs)
{
	if(iFoil<0 || iFoil>=FOIL_COUNT) return;
	vecFoilBegin[iFoil] = iOffs;
}

void TofConfig::SetImagesPerFoil(int iNumImagesPerFoil)
{ IMAGES_PER_FOIL = iNumImagesPerFoil; }
void TofConfig::SetImageCount(int iImgCount)
{ IMAGE_COUNT = iImgCount; }
void TofConfig::SetPseudoCompression(bool bSet)
{ USE_PSEUDO_COMPRESSION = bSet; }
void TofConfig::SetSumFirstAndLast(bool bSet)
{ SUM_FIRST_AND_LAST = bSet; }
void TofConfig::SetNumOscillations(double dVal)
{ NUM_OSC = dVal; CheckNumOscillations(); }



void PadConfig::CheckPadArguments(int* piStartX, int* piEndX,
								  int* piStartY, int* piEndY) const
{
	if(piStartX && piEndX && piStartY && piEndY)
	{
		if(*piStartX>*piEndX)
		{ int iTmp = *piStartX; *piStartX = *piEndX; *piEndX = iTmp; }
		if(*piStartY>*piEndY)
		{ int iTmp = *piStartY; *piStartY = *piEndY; *piEndY = iTmp; }

		if(*piStartX<0)
			*piStartX = 0;
		else if(*piStartX>GetImageWidth())
			*piStartX = GetImageWidth();
		if(*piEndX<0)
			*piEndX = 0;
		else if(*piEndX>GetImageWidth())
			*piEndX = GetImageWidth();

		if(*piStartY<0)
			*piStartY = 0;
		else if(*piStartY>GetImageHeight())
			*piStartY = GetImageHeight();
		if(*piEndY<0)
			*piEndY = 0;
		else if(*piEndY>GetImageHeight())
			*piEndY = GetImageHeight();
	}
}

void TofConfig::CheckTofArguments(int* piStartX, int* piEndX, int* piStartY,
								  int* piEndY, int* piFolie, int* piZ) const
{
	CheckPadArguments(piStartX, piEndX, piStartY, piEndY);

	if(piFolie)
	{
		if(*piFolie<0)
			*piFolie=0;
		if(*piFolie >= FOIL_COUNT)
			*piFolie = FOIL_COUNT-1;

	}
	if(piZ)
	{
		if(*piZ<0)
			*piZ = 0;
		if(*piZ >= IMAGES_PER_FOIL)
			*piZ = IMAGES_PER_FOIL-1;
	}
}

//------------------------------------------------------------------------------
// exp config

ExpConfig::ExpConfig() : m_strBaseDir("."), m_iNumExp(0), m_iYear(-1)
{}

void ExpConfig::SetBaseDir(const std::string& strDir) { m_strBaseDir = strDir; }

std::string ExpConfig::GetBaseDir()
{
	std::string strRet = m_strBaseDir;

	if(m_iYear < 0) SetCurYear();

	std::ostringstream ostrYear;
	std::ostringstream ostrNumExp;

	ostrYear << m_iYear;
	ostrNumExp << m_iNumExp;

	find_and_replace(strRet, "${year}", ostrYear.str());
	find_and_replace(strRet, "${proposal_num}", ostrNumExp.str());

	//std::cout << strRet << std::endl;
	return strRet;
}

void ExpConfig::SetCurYear()
{
	time_t t;
	time(&t);
	tm* ptm = localtime(&t);

	m_iYear = 1900 + ptm->tm_year;
}

//------------------------------------------------------------------------------
// instrument config

InstrumentConfig::InstrumentConfig()
		: m_dDetectorLenX(0.2), m_dDetectorLenY(0.2),
		  m_dDetectorCenterX(0.1), m_dDetectorCenterY(0.1),
		  m_dLs(0.9), m_dLam(4.8), m_dOmegaM(10000.)
{}


//------------------------------------------------------------------------------
// global config

TofConfig GlobalConfig::s_config = TofConfig();
ExpConfig GlobalConfig::s_expconfig = ExpConfig();
InstrumentConfig GlobalConfig::s_instrconfig = InstrumentConfig();

int GlobalConfig::iPhaseBlockSize[2] = {1, 2};
int GlobalConfig::iContrastBlockSize[2] = {1, 2};
double GlobalConfig::LOG_LOWER_RANGE = -0.5;

// Defaults used in ROOT::Minuit2::MnApplication::operator()
double GlobalConfig::dMinuitTolerance = 0.1;
unsigned int GlobalConfig::uiMinuitMaxFcn = 0;
int GlobalConfig::iMinuitAlgo = MINUIT_MIGRAD;
unsigned int GlobalConfig::uiMinuitStrategy = 1;
unsigned int GlobalConfig::uiMinCountsToFit = 50;

bool GlobalConfig::bUseFFT = 0;
int GlobalConfig::iShiftMethod = /*SHIFT_SINE_ONLY*/ SHIFT_ZERO_ORDER;

bool GlobalConfig::bGuessConfig = 0;
bool GlobalConfig::bDumpFiles = 0;

std::string GlobalConfig::m_strCurDir;

void GlobalConfig::Init()
{
#ifdef __BIG_ENDIAN__
	logger.SetCurLogLevel(LOGLEVEL_INFO);
	logger << "Globals: This is a PowerPC (big endian).\n";
#endif

#ifndef USE_MINUIT
	logger.SetCurLogLevel(LOGLEVEL_ERR);
	logger << "Globals: Minuit not available." << "\n";
#endif

	Deinit();


// Cascade-Qt-Client l��dt Einstellungen ��ber XML-Datei
#ifdef __CASCADE_QT_CLIENT__

	//--------------------------------------------------------------------------
	// logger
	int iLogToFile = Config::GetSingleton()->QueryInt(
						"/cascade_config/log/log_to_file", 0);
	if(iLogToFile)
	{
		std::string strLogFile =
			Config::GetSingleton()->QueryString("/cascade_config/log/file",
												"cascade.log");
		logger.Init(strLogFile.c_str());
	}

	int iLogLevel = Config::GetSingleton()->QueryInt(
						"/cascade_config/log/level", LOGLEVEL_INFO);
	SetLogLevel(iLogLevel);

	bool bRepeatLogs = Config::GetSingleton()->QueryInt(
						"/cascade_config/log/repeat_duplicate_logs", 1);
	SetRepeatLogs(bRepeatLogs);
	//--------------------------------------------------------------------------


	//--------------------------------------------------------------------------
	// TOF / PAD stuff
	bGuessConfig = (bool)Config::GetSingleton()->QueryInt(
				"/cascade_config/tof_file/guess_file_config", bGuessConfig);

	s_config.IMAGE_COUNT = Config::GetSingleton()->QueryInt(
				"/cascade_config/tof_file/image_count", s_config.IMAGE_COUNT);
	s_config.FOIL_COUNT = Config::GetSingleton()->QueryInt(
				"/cascade_config/tof_file/foil_count", s_config.FOIL_COUNT);
	s_config.IMAGES_PER_FOIL = Config::GetSingleton()->QueryInt(
				"/cascade_config/tof_file/images_per_foil",
													 s_config.IMAGES_PER_FOIL);
	s_config.IMAGE_WIDTH = Config::GetSingleton()->QueryInt(
				"/cascade_config/tof_file/image_width", s_config.IMAGE_WIDTH);
	s_config.IMAGE_HEIGHT = Config::GetSingleton()->QueryInt(
				"/cascade_config/tof_file/image_height", s_config.IMAGE_HEIGHT);
	s_config.USE_PSEUDO_COMPRESSION = Config::GetSingleton()->QueryInt(
				"/cascade_config/tof_file/pseudo_compression",
				s_config.USE_PSEUDO_COMPRESSION);
	s_config.SUM_FIRST_AND_LAST = Config::GetSingleton()->QueryInt(
				"/cascade_config/tof_file/sum_first_and_last",
				s_config.SUM_FIRST_AND_LAST);
	s_config.NUM_OSC = Config::GetSingleton()->QueryDouble(
				"/cascade_config/tof_file/number_of_oscillations",
				s_config.NUM_OSC);
	s_config.CheckNumOscillations();

	s_config.vecFoilBegin.resize(s_config.FOIL_COUNT);
	for(int i=0; i<s_config.FOIL_COUNT; ++i)
	{
		char pcStr[256];
		sprintf(pcStr, "/cascade_config/tof_file/foil_%d_start", i+1);
		s_config.vecFoilBegin[i] = (Config::GetSingleton()->QueryInt(
				pcStr, s_config.IMAGES_PER_FOIL*2*i));
	}
	//--------------------------------------------------------------------------


	//--------------------------------------------------------------------------
	// graphs
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
	//--------------------------------------------------------------------------


	//--------------------------------------------------------------------------
	// fitter
	dMinuitTolerance = Config::GetSingleton()->QueryDouble(
				"/cascade_config/minuit/tolerance", dMinuitTolerance);
	uiMinuitMaxFcn = (unsigned int)Config::GetSingleton()->QueryInt(
				"/cascade_config/minuit/maxfcn", uiMinuitMaxFcn);
	uiMinuitStrategy = (unsigned int)Config::GetSingleton()->QueryInt(
				"/cascade_config/minuit/strategy", uiMinuitStrategy);
	uiMinCountsToFit = (unsigned int)Config::GetSingleton()->QueryInt(
				"/cascade_config/minuit/min_counts", uiMinCountsToFit);

	bUseFFT = (Config::GetSingleton()->QueryInt(
				"/cascade_config/fourier/use_fft_method_instead", bUseFFT) != 0);
	iShiftMethod = Config::GetSingleton()->QueryInt(
				"/cascade_config/fourier/phase_correction", iShiftMethod);

	std::string strAlgo =
		Config::GetSingleton()->QueryString("/cascade_config/minuit/algo",
											"migrad");
	if(strcasecmp(strAlgo.c_str(), "migrad")==0)
		iMinuitAlgo = MINUIT_MIGRAD;
	else if(strcasecmp(strAlgo.c_str(), "minimize")==0)
		iMinuitAlgo = MINUIT_MINIMIZE;
	else if(strcasecmp(strAlgo.c_str(), "simplex")==0)
		iMinuitAlgo = MINUIT_SIMPLEX;
	else
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Globals: Unknown algorithm: \"" << strAlgo << "\".\n";
	}

	bDumpFiles = (bool)Config::GetSingleton()->QueryInt(
				"/cascade_config/log/dump_files", bDumpFiles);

	
	//--------------------------------------------------------------------------

	s_instrconfig.m_dDetectorLenX = Config::GetSingleton()->QueryDouble(
					"/cascade_config/instrument/detector_length_x",
					s_instrconfig.m_dDetectorLenX);
	s_instrconfig.m_dDetectorLenY = Config::GetSingleton()->QueryDouble(
					"/cascade_config/instrument/detector_length_y",
					s_instrconfig.m_dDetectorLenY);

	s_instrconfig.m_dDetectorCenterX = Config::GetSingleton()->QueryDouble(
					"/cascade_config/instrument/detector_center_x",
					s_instrconfig.m_dDetectorCenterX);
	s_instrconfig.m_dDetectorCenterY = Config::GetSingleton()->QueryDouble(
					"/cascade_config/instrument/detector_center_y",
					s_instrconfig.m_dDetectorCenterY);

	s_instrconfig.m_dLs = Config::GetSingleton()->QueryDouble(
									"/cascade_config/instrument/Ls",
									s_instrconfig.m_dLs);

	s_instrconfig.m_dLam = Config::GetSingleton()->QueryDouble(
									"/cascade_config/instrument/lambda",
									s_instrconfig.m_dLam);
	
	s_instrconfig.m_dOmegaM = Config::GetSingleton()->QueryDouble(
									"/cascade_config/instrument/omega_M",
									s_instrconfig.m_dOmegaM);

	
	//--------------------------------------------------------------------------
	// initial directory

	s_expconfig.SetBaseDir(Config::GetSingleton()->
					QueryString("/cascade_config/dirs/exp_base_dir", "."));
	s_expconfig.SetNumExp(Config::GetSingleton()->QueryInt(
				"/cascade_config/dirs/proposal_num", 0));
	//--------------------------------------------------------------------------

#else	// Nicos-Client holt Einstellungen von Detektor

	// Defaults setzen
	s_config.vecFoilBegin.resize(s_config.FOIL_COUNT);
	for(int i=0; i<s_config.FOIL_COUNT; ++i)
		s_config.vecFoilBegin[i] = (s_config.IMAGES_PER_FOIL*2*i); /*default*/

	/// \todo richtige Einstellungen holen oder mit den Setter-Funktionen setzen
#endif
}

void GlobalConfig::Deinit()
{}

// ***************************** Getter & Setter *******************************
double GlobalConfig::GetLogLowerRange() { return LOG_LOWER_RANGE; }

unsigned int GlobalConfig::GetMinuitMaxFcn() { return uiMinuitMaxFcn; }
double GlobalConfig::GetMinuitTolerance() { return dMinuitTolerance; }
int GlobalConfig::GetMinuitAlgo() { return iMinuitAlgo; }
unsigned int GlobalConfig::GetMinuitStrategy() { return uiMinuitStrategy; }
unsigned int GlobalConfig::GetMinCountsToFit() { return uiMinCountsToFit; }

bool GlobalConfig::GetUseFFT() { return bUseFFT; }
int GlobalConfig::GetShiftMethod() { return iShiftMethod; }

TofConfig& GlobalConfig::GetTofConfig() { return s_config;}
ExpConfig& GlobalConfig::GetExpConfig() { return s_expconfig; }
InstrumentConfig& GlobalConfig::GetInstrConfig() { return s_instrconfig; }
bool GlobalConfig::GetDumpFiles() { return bDumpFiles; }

const std::string& GlobalConfig::GetCurDir() { return m_strCurDir; }

void GlobalConfig::SetMinuitMaxFnc(unsigned int uiMaxFcn)
{ uiMinuitMaxFcn = uiMaxFcn; }
void GlobalConfig::SetMinuitTolerance(double dTolerance)
{ dMinuitTolerance = dTolerance; }
void GlobalConfig::SetMinuitAlgo(int iAlgo)
{ iMinuitAlgo = iAlgo; }
void GlobalConfig::SetMinuitStrategy(unsigned int uiStrategy)
{ uiMinuitStrategy = uiStrategy; }
void GlobalConfig::SetMinCountsToFit(unsigned int uiCts)
{ uiMinCountsToFit = uiCts; }

void GlobalConfig::SetUseFFT(bool bUse)
{ bUseFFT = bUse; }
void GlobalConfig::SetShiftMethod(int iMethod)
{ iShiftMethod = iMethod; }

void GlobalConfig::SetLogLevel(int iLevel)
{ logger.SetLogLevel(iLevel); }
void GlobalConfig::SetRepeatLogs(bool bRepeat)
{ logger.SetRepeatLogs(bRepeat); }

void GlobalConfig::SetCurDir(const std::string& strDir) { m_strCurDir = strDir; }
// *****************************************************************************

bool GlobalConfig::GuessConfigFromSize(bool bPseudoCompressed, int iLen,
											bool bIsTof, bool bFirstCall)
{
	if(!bGuessConfig)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Please configure the loader correctly using either"
				  " GlobalConfig or the config file."
			   << " Alternatively you can enable \"guess_file_config\" in "
				  "the config file for testing."
			   << "\n";

		return false;
	}

	if(bFirstCall)
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "Globals: Trying to guess correct configuration."
			   " (Please configure the loader correctly using either"
			   " GlobalConfig or the config file.)"
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
			s_config.IMAGE_WIDTH = iKnownX[i];
			s_config.IMAGE_HEIGHT = iKnownY[i];
			s_config.IMAGE_COUNT = iKnownCnt[i];
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
					s_config.IMAGE_COUNT = iImgCnt;
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
					s_config.IMAGE_COUNT = iImgCnt;
					break;
				}
			}
		}

		if(bFound)
		{
			logger.SetCurLogLevel(LOGLEVEL_WARN);
			logger << "Globals: Guessing image count: "
				   << s_config.IMAGE_COUNT << "\n";
		}
		return bFound;
	}
	else if(bIsTof && bPseudoCompressed)
	{
		// TODO
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Globals: Pseudo-compressed size guess not yet implemented.\n";
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
			s_config.IMAGE_WIDTH = iKnownX[i];
			s_config.IMAGE_HEIGHT = iKnownY[i];
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
						s_config.IMAGE_WIDTH = iSideLenX;
						s_config.IMAGE_HEIGHT = iSideLenY;
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
						s_config.IMAGE_WIDTH = i;
						s_config.IMAGE_HEIGHT = j;
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
			logger << "Globals: Guessing image width: "
				   << s_config.IMAGE_WIDTH << "\n";
			logger << "Globals: Guessing image height: "
				   << s_config.IMAGE_HEIGHT << "\n";
		}

		return bFound;
	}
}
// *****************************************************************************
