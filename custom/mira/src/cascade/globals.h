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

// use minuit for fits?
#define USE_MINUIT
// #define USE_BOOST

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

		static bool bGuessConfig;

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

		static TofConfig& GetTofConfig();
		//----------------------------------------------------------------------

		//----------------------------------------------------------------------
		// setter
		static void SetMinuitMaxFnc(unsigned int uiMaxFcn);
		static void SetMinuitTolerance(double dTolerance);
		static void SetMinuitAlgo(int iAlgo);
		static void SetMinuitStrategy(unsigned int iStrategy);
		//----------------------------------------------------------------------

		static void SetLogLevel(int iLevel);
		static void SetRepeatLogs(bool bRepeat);
};

#endif
