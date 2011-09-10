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
// Klassen zum Laden und Verarbeiten von Tof- & Pad-Dateien

#ifndef __TOFLOADER__
#define __TOFLOADER__

// use minuit for fits?
#define USE_MINUIT

#ifndef NULL
	#define NULL	0
#endif

class TmpImage;
class TmpGraph;
class TofImage;
class PadImage;

#define LOAD_SUCCESS		 1
#define LOAD_FAIL			 0
#define LOAD_SIZE_MISMATCH	-1

#define MINUIT_SIMPLEX 	1
#define MINUIT_MINIMIZE	2
#define MINUIT_MIGRAD 	3

#define TOF_COMPRESSION_NONE 			0
#define TOF_COMPRESSION_PSEUDO 			1
#define TOF_COMPRESSION_USEGLOBCONFIG 	2

//==============================================================================

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

/*
 * PAD
 * container representing a PAD image
 * (corresponds to the "IMAGE" measurement type in the server & HardwareLib)
 */
class PadImage
{
	friend class TmpImage;

	protected:
		// actual data
		unsigned int *m_puiDaten;

		// lower & upper bound values
		int m_iMin, m_iMax;

		// PAD data stored in external memory which needs no management,
		// i.e. allocation & freeing?
		bool m_bExternalMem;

		// clean up
		void Clear(void);

	public:
		// create PAD from file (or empty PAD otherwise)
		PadImage(const char *pcFileName=NULL, bool bExternalMem=false);

		// create PAD from other PAD
		PadImage(const PadImage& pad);

		virtual ~PadImage();

		// set pointer to external memory (if bExternalMem==true)
		void SetExternalMem(void* pvDaten);

		// size (in ints) of PAD image
		int GetPadSize() const;

		int LoadFile(const char *pcFileName);

		// load PAD from memory
		// uiBufLen: # of ints (NOT # of bytes)
		int LoadMem(const unsigned int *puiBuf, unsigned int uiBufLen);

		// calculate lower & upper bound values
		void UpdateRange();

		// print PAD as text
		void Print(const char* pcOutFile=NULL);

		// get specific point
		unsigned int GetData(int iX, int iY) const;

		// get pointer to internal memory
		unsigned int* GetRawData(void);

		// total number of counts
		unsigned int GetCounts() const;

		// total number of counts in given region of interest
		unsigned int GetCounts(int iStartX, int iEndX,
							   int iStartY, int iEndY) const;
};


//==============================================================================

/*
 * class for temporary images generated by some methods of the
 * TofImage class
 */
class TmpImage
{
	friend class PadImage;
	friend class TofImage;

  protected:
	// image dimensions
	int m_iW, m_iH;

	//--------------------------------------------------------------------------
	// only one of the following pointers is actually used (the other has
	// to be NULL)

	// pointer to array for counts data
	unsigned int* m_puiDaten;
	// pointer to array for contrast/phase data
	double* m_pdDaten;
	//--------------------------------------------------------------------------

	// lower & upper bound values
	double m_dMin, m_dMax;

  public:
	// create EMPTY TmpImage without allocation any memory etc.
	// (which done externally)
	TmpImage();

	// create TmpImage from other TmpImage; does allocate memory
	TmpImage(const TmpImage& tmp);

	virtual ~TmpImage();

	// clean up
	void Clear(void);

	// get data point (if "wrong" type is requested, the return value is cast)
	double GetData(int iX, int iY) const;
	unsigned int GetIntData(int iX, int iY) const;

	int GetWidth() const;
	int GetHeight() const;

	// calculate lower & upper bound values
	void UpdateRange();

	// write XML representation of image
	bool WriteXML(const char* pcFileName) const;

	// create TmpImage from PAD image
	void ConvertPAD(PadImage* pPad);

	// adds another TmpImage to this one
	void Add(const TmpImage& tmp);
};


//==============================================================================

/*
 * class for temporary graph data generated by some methods of the
 * TofImage class
 */
class TmpGraph
{
  friend class TofImage;

  protected:
	// # of data points
	int m_iW;

	// pointer to data array
	unsigned int* m_puiDaten;

  public:
	// create empty graph (does not allocate memory)
	TmpGraph();
	virtual ~TmpGraph();

	// fit a sinus function to the data points
	// return value: fit successful?
	bool FitSinus(double &dPhase, double &dScale,
				  double &dAmp, double &dOffs) const;

	//--------------------------------------------------------------------------
	// getter
	unsigned int GetData(int iX) const;
	int GetWidth(void) const;
	int GetMin() const;
	int GetMax() const;
	//--------------------------------------------------------------------------

	// is sum of data points < iTotal?
	bool IsLowerThan(int iTotal) const;
};


//==============================================================================

/*
 * TOF
 * container representing a TOF image
 * (corresponds to the "TOF" measurement type in the server & HardwareLib)
 */
class TofImage
{
	protected:
		// pointer to data array (format depends on compression used)
		unsigned int *m_puiDaten;
		bool m_bPseudoCompressed;

		// TOF data stored in external memory which needs no management,
		// i.e. allocation & freeing?
		bool m_bExternalMem;

	public:
		//----------------------------------------------------------------------
		// "internal" methods => use corresponding method below
		void GetROI(int iStartX, int iEndX, int iStartY, int iEndY, int iFoil,
					int iTimechannel, TmpImage *pImg) const;
		void GetGraph(int iStartX, int iEndX, int iStartY, int iEndY,
					  int iFoil, TmpGraph* pGraph) const;
		void GetTotalGraph(int iStartX, int iEndX, int iStartY, int iEndY,
						   double dPhaseShift ,TmpGraph* pGraph) const;
		void GetOverview(TmpImage *pImg) const;
		void GetPhaseGraph(int iFoil, TmpImage *pImg, int iStartX, int iEndX,
						   int iStartY, int iEndY, bool bInDeg=true) const;
		void GetPhaseGraph(int iFoil, TmpImage *pImg, bool bInDeg=true) const;
		void GetContrastGraph(int iFoil, TmpImage *pImg, int iStartX, int iEndX,
							  int iStartY, int iEndY) const;
		void GetContrastGraph(int iFoil, TmpImage *pImg) const;

		void AddFoils(int iBits, int iChannelBits/*=0xffffffff*/,
					  TmpImage *pImg) const;
		void AddFoils(const bool *pbChannels, TmpImage *pImg) const;
		void AddPhases(const bool *pbFoils, TmpImage *pImg) const;
		void AddContrasts(const bool *pbFoils, TmpImage *pImg) const;
		//----------------------------------------------------------------------

	public:
		TofImage(const char *pcFileName=NULL,
				 int iCompression=TOF_COMPRESSION_USEGLOBCONFIG,
				 bool bExternalMem=false);

		virtual ~TofImage();

		// set pointer to external memory (if bExternalMem==true)
		void SetExternalMem(void* pvDaten);

		int GetTofSize() const;
		void Clear();
		int GetCompressionMethod() const;
		void SetCompressionMethod(int iComp);

		// get specific count value
		unsigned int GetData(int iFoil, int iTimechannel, int iX, int iY) const;
		unsigned int GetData(int iImage, int iX, int iY) const;

		// get raw pointer to data array
		unsigned int* GetRawData(void) const;

		int LoadFile(const char *pcFileName);

		// uiBufLen: # of ints (NOT # of bytes)
		int LoadMem(const unsigned int *puiBuf, unsigned int uiBufLen);

		// get total counts
		unsigned int GetCounts() const;

		// get total counts in specific region of interest
		unsigned int GetCounts(int iStartX, int iEndX,
							   int iStartY, int iEndY) const;

		//----------------------------------------------------------------------
		// copy ROI into new temporary image
		TmpImage GetROI(int iStartX, int iEndX, int iStartY, int iEndY,
						int iFoil, int iTimechannel) const;

		// get graph for counts vs. time channels
		TmpGraph GetGraph(int iStartX, int iEndX, int iStartY, int iEndY,
						  int iFoil) const;

		// TODO
		TmpGraph GetTotalGraph(int iStartX, int iEndX, int iStartY, int iEndY,
							   double dPhaseShift) const;

		// get overview image (summing all individual images in TOF)
		TmpImage GetOverview() const;

		// phase image
		TmpImage GetPhaseGraph(int iFoil, int iStartX, int iEndX, int iStartY,
							   int iEndY, bool bInDeg=true) const;

		// contrast image
		TmpImage GetContrastGraph(int iFoil, int iStartX, int iEndX,
								  int iStartY, int iEndY) const;

		// sum foils/phases/contrasts marked in respective bool array
		TmpImage AddFoils(const bool *pbChannels) const;
		TmpImage AddPhases(const bool *pbFoils) const;
		TmpImage AddContrasts(const bool *pbFoils) const;
		//----------------------------------------------------------------------
};

#endif
