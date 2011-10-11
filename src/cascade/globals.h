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

#ifndef __GLOBALS__
#define __GLOBALS__

#include "tofloader.h"

/*
 * global, static configuration class
 * used to configure layout of TOF & PAD formats etc. before first use of
 * these classes
 */
class Config_TofLoader
{
	friend class TofImage;

	protected:
		// how many foils in TOF images
		static int FOIL_COUNT;

		// how many time channels per foil in TOF?
		static int IMAGES_PER_FOIL;

		// width & height of PAD and TOF images
		static int IMAGE_WIDTH;
		static int IMAGE_HEIGHT;

		// total image count in TOF
		static int IMAGE_COUNT;

		// array of indices marking the beginning of the individual foils
		static int *piFoilBegin;

		// width & height of blocks used for calculation phase or
		// constrast images
		static int iPhaseBlockSize[2];
		static int iContrastBlockSize[2];

		static double LOG_LOWER_RANGE;

		// does server use "pseudo-compression" i.e. remove zero images between
		// foils and add first and last time channel?
		static bool USE_PSEUDO_COMPRESSION;

		// parameters for minuit minimizer
		static double dMinuitTolerance;
		static unsigned int uiMinuitMaxFcn;
		static int iMinuitAlgo;
		static unsigned int uiMinuitStrategy;

	public:
		// iLen in Ints, nicht Bytes
		static bool GuessConfigFromSize(bool bPseudoCompressed, int iLen,
										bool bIsTof, bool bFirstCall=true);
		static void Init();
		static void Deinit();

		//----------------------------------------------------------------------
		// getter
		static double GetLogLowerRange();
		static int GetFoilCount();
		static int GetImagesPerFoil();
		static int GetImageWidth();
		static int GetImageHeight();
		static int GetImageCount();
		static int GetFoilBegin(int iFoil);
		static bool GetPseudoCompression();
		static unsigned int GetMinuitMaxFcn();
		static double GetMinuitTolerance();
		static int GetMinuitAlgo();
		static unsigned int GetMinuitStrategy();
		//----------------------------------------------------------------------

		//----------------------------------------------------------------------
		// setter
		static void SetFoilCount(int iNumFoils);
		static void SetImagesPerFoil(int iNumImagesPerFoil);
		static void SetImageWidth(int iImgWidth);
		static void SetImageHeight(int iImgHeight);
		static void SetImageCount(int iImgCount);
		static void SetFoilBegin(int iFoil, int iOffs);
		static void SetPseudoCompression(bool bSet);
		static void SetMinuitMaxFnc(unsigned int uiMaxFcn);
		static void SetMinuitTolerance(double dTolerance);
		static void SetMinuitAlgo(int iAlgo);
		static void SetMinuitStrategy(unsigned int iStrategy);
		//----------------------------------------------------------------------

		// check & correct argument ranges
		static void CheckArguments(int* piStartX, int* piEndX, int* piStartY,
								   int* piEndY, int* piFoil=0,
								   int* piTimechannel=0);

		static void SetLogLevel(int iLevel);
		static void SetRepeatLogs(bool bRepeat);
};

//==============================================================================

#endif
