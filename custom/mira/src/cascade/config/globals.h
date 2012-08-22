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

#ifndef __GLOBALS__
#define __GLOBALS__

#include <vector>
#include <string>

// use minuit for fits?
#define USE_MINUIT

#ifdef __CASCADE_QT_CLIENT__
	#define USE_FFTW
	//#define USE_BOOST
	#define USE_XML
#endif

#define LOAD_SUCCESS		 1
#define LOAD_FAIL			 0
#define LOAD_SIZE_MISMATCH	-1

#define SAVE_SUCCESS		 1
#define SAVE_FAIL			 0

#define MINUIT_SIMPLEX 	1
#define MINUIT_MINIMIZE	2
#define MINUIT_MIGRAD 	3

#ifndef NULL
	#define NULL	0
#endif

#define SHIFT_SINE_ONLY		-1
#define SHIFT_ZERO_ORDER	0
#define SHIFT_FIRST_ORDER	1

class GlobalConfig;

/*
 * configuration of PAD class
 */
class PadConfig
{
	friend class GlobalConfig;

	protected:
		// width & height of PAD and TOF images
		int IMAGE_WIDTH;
		int IMAGE_HEIGHT;

	public:
		PadConfig();
		PadConfig(const PadConfig& conf);

		virtual const PadConfig& operator=(const PadConfig& conf);

		//----------------------------------------------------------------------
		// getter
		int GetImageWidth() const;
		int GetImageHeight() const;

		//----------------------------------------------------------------------
		// setter
		void SetImageWidth(int iImgWidth);
		void SetImageHeight(int iImgHeight);

		// check & correct argument ranges
		void CheckPadArguments(int* piStartX, int* piEndX,
									  int* piStartY, int* piEndY) const;
};

/*
 * configuration of TOF class
 */
class TofConfig : public PadConfig
{
	friend class GlobalConfig;

	protected:
		// how many foils in TOF images
		int FOIL_COUNT;

		// how many time channels per foil in TOF?
		int IMAGES_PER_FOIL;

		// total image count in TOF
		int IMAGE_COUNT;

		// vector of indices marking the beginning of the individual foils
		std::vector<int> vecFoilBegin;

		bool USE_PSEUDO_COMPRESSION;
		bool SUM_FIRST_AND_LAST;

		double NUM_OSC;

		void CheckNumOscillations();

	public:
		TofConfig();
		TofConfig(const TofConfig& conf);

		virtual const TofConfig& operator=(const TofConfig& conf);

		//----------------------------------------------------------------------
		// getter
		int GetFoilCount() const;
		int GetImagesPerFoil() const;
		int GetImageCount() const;			// TOTAL images in TOF
		int GetFoilBegin(int iFoil) const;
		bool GetPseudoCompression() const;
		bool GetSumFirstAndLast() const;
		double GetNumOscillations() const;

		//----------------------------------------------------------------------
		// setter
		void SetFoilCount(int iNumFoils);
		void SetImagesPerFoil(int iNumImagesPerFoil);
		void SetImageCount(int iImgCount);	// TOTAL images in TOF
		void SetFoilBegin(int iFoil, int iOffs);
		void SetPseudoCompression(bool bSet);
		void SetSumFirstAndLast(bool bSet);
		void SetNumOscillations(double dVal);

		// check & correct argument ranges
		void CheckTofArguments(int* piStartX, int* piEndX,
							   int* piStartY, int* piEndY,
							   int* piFoil=0, int* piTimechannel=0) const;
};

class ExpConfig
{
	protected:
		std::string m_strBaseDir;
		int m_iNumExp;
		int m_iYear;

	public:
		ExpConfig();

		std::string GetBaseDir();
		void SetBaseDir(const std::string& strDir);

		void SetNumExp(int iExp) { m_iNumExp = iExp; }
		int GetNumExp() const { return m_iNumExp; }

		void SetCurYear();
		void SetYear(int iYear) { m_iYear = iYear; }
		int GetYear() const { return m_iYear; }
};

/*
 * global, static configuration class
 * used to configure layout of TOF & PAD formats etc. before first use of
 * these classes
 */
class GlobalConfig
{
	friend class TofImage;

	protected:
		static TofConfig s_config;
		static ExpConfig s_expconfig;

		// width & height of blocks used for calculation phase or
		// constrast images
		static int iPhaseBlockSize[2];
		static int iContrastBlockSize[2];

		static double LOG_LOWER_RANGE;

		// parameters for minuit minimizer
		static double dMinuitTolerance;
		static unsigned int uiMinuitMaxFcn;
		static int iMinuitAlgo;
		static unsigned int uiMinuitStrategy;

		static unsigned int uiMinCountsToFit;
		
		static bool bUseFFT;
		static int iShiftMethod;

		static bool bGuessConfig;
		static bool bDumpFiles;

		static std::string m_strCurDir;

	public:
		// iLen in Ints, nicht Bytes
		static bool GuessConfigFromSize(bool bPseudoCompressed, int iLen,
										bool bIsTof, bool bFirstCall=true);
		static void Init();
		static void Deinit();

		//----------------------------------------------------------------------
		// getter
		static double GetLogLowerRange();
		static unsigned int GetMinuitMaxFcn();
		static double GetMinuitTolerance();
		static int GetMinuitAlgo();
		static unsigned int GetMinuitStrategy();
		static unsigned int GetMinCountsToFit();
		
		static bool GetUseFFT();
		static int GetShiftMethod();

		static const std::string& GetCurDir();

		static TofConfig& GetTofConfig();
		static ExpConfig& GetExpConfig();

		static bool GetDumpFiles();
		//----------------------------------------------------------------------

		//----------------------------------------------------------------------
		// setter
		static void SetMinuitMaxFnc(unsigned int uiMaxFcn);
		static void SetMinuitTolerance(double dTolerance);
		static void SetMinuitAlgo(int iAlgo);
		static void SetMinuitStrategy(unsigned int iStrategy);
		static void SetMinCountsToFit(unsigned int iMinCts);
		
		static void SetUseFFT(bool bUse);
		static void SetShiftMethod(int iMethod);

		static void SetCurDir(const std::string& strDir);
		//----------------------------------------------------------------------

		static void SetLogLevel(int iLevel);
		static void SetRepeatLogs(bool bRepeat);
};

#endif
