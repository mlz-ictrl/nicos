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

#ifndef __TOFLOADER__
#define __TOFLOADER__

#define USE_MINUIT		// Minuit für Fits benutzen?

#ifndef NULL
	#define NULL	0
#endif

class TmpImage;
class TmpGraph;
class TofImage;
class PadImage;


#define MINUIT_SIMPLEX 	1
#define MINUIT_MINIMIZE	2
#define MINUIT_MIGRAD 	3

// Konfiguration
class Config_TofLoader
{
	friend class TofImage;

	protected:
		static int FOIL_COUNT;

		// wieviele Zeitkanaele pro Folie?
		static int IMAGES_PER_FOIL;

		static int IMAGE_WIDTH;
		static int IMAGE_HEIGHT;
		static int IMAGE_COUNT;

		// Folienbeginn
		static int *piFoilBegin;

		static int iPhaseBlockSize[2];
		static int iContrastBlockSize[2];

		static double LOG_LOWER_RANGE;

		// sind Null-Bilder schon von Server entfernt und Folienadditionen gemacht worden?
		static bool USE_PSEUDO_COMPRESSION;

		static double dMinuitTolerance;
		static unsigned int uiMinuitMaxFcn;
		static int iMinuitAlgo;
		static unsigned int uiMinuitStrategy;

	public:
		// iLen in Ints, nicht Bytes
		static bool GuessConfigFromSize(bool bPseudoCompressed, int iLen, bool bIsTof, bool bFirstCall=true);
		static void Init();
		static void Deinit();

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

		static void CheckArguments(int* piStartX, int* piEndX, int* piStartY, int* piEndY, int* piFoil=0, int* piTimechannel=0);

		static void SetLogLevel(int iLevel);
		static void SetRepeatLogs(bool bRepeat);
};


#define LOAD_SUCCESS		 1
#define LOAD_FAIL			 0
#define LOAD_SIZE_MISMATCH	-1

// PAD-Bilder
class PadImage
{
	friend class TmpImage;

	protected:
		unsigned int *m_puiDaten;
		int m_iMin, m_iMax;
		bool m_bExternalMem;

		void Clear(void);

	public:
		PadImage(const char *pcFileName=NULL, bool bExternalMem=false);
		PadImage(const PadImage& pad);
		virtual ~PadImage();

		void SetExternalMem(void* pvDaten);
		int GetPadSize() const;

		int LoadFile(const char *pcFileName);
		// uiBufLen: Anzahl Ints (nicht Anzahl Bytes)
		int LoadMem(const unsigned int *puiBuf, unsigned int uiBufLen);

		void UpdateRange();
		void Print(const char* pcOutFile=NULL);

		unsigned int GetData(int iX, int iY) const;
		unsigned int* GetRawData(void);

		unsigned int GetCounts() const;
		unsigned int GetCounts(int iStartX, int iEndX, int iStartY, int iEndY) const;
};

// Klasse, um Zwischenbilder zu verwalten
class TmpImage
{
	friend class PadImage;
	friend class TofImage;

  protected:
	int m_iW, m_iH;
	unsigned int* m_puiDaten;	// für Counts-Diagramm
	double* m_pdDaten;			// für Phasen- und Kontrastdiagramm
	double m_dMin, m_dMax;

  public:
	TmpImage();
	TmpImage(const TmpImage& tmp);
	virtual ~TmpImage();

	void Clear(void);

	double GetData(int iX, int iY) const;
	unsigned int GetIntData(int iX, int iY) const;

	int GetWidth() const;
	int GetHeight() const;

	void UpdateRange();
	bool WriteXML(const char* pcFileName) const;
	void ConvertPAD(PadImage* pPad);

	void Add(const TmpImage& tmp);
};

// Klasse für temporäre Graph-Daten
class TmpGraph
{
  friend class TofImage;

  protected:
	int m_iW;
	unsigned int* m_puiDaten;

  public:

	TmpGraph();
	virtual ~TmpGraph();

	bool FitSinus(double &dPhase, double &dScale, double &dAmp, double &dOffs) const;

	unsigned int GetData(int iX) const;
	int GetWidth(void) const;
	int GetMin() const;
	int GetMax() const;

	bool IsLowerThan(int iTotal) const;
};

#define TOF_COMPRESSION_NONE 			0
#define TOF_COMPRESSION_PSEUDO 			1
#define TOF_COMPRESSION_USEGLOBCONFIG 	2

// TOF-Bilder
class TofImage
{
	protected:
		unsigned int *m_puiDaten;
		bool m_bPseudoCompressed;
		bool m_bExternalMem;

	public:
		TofImage(const char *pcFileName=NULL, int iCompression=TOF_COMPRESSION_USEGLOBCONFIG, bool bExternalMem=false);
		virtual ~TofImage();

		void SetExternalMem(void* pvDaten);
		int GetTofSize() const;
		void Clear();
		int GetCompressionMethod() const;
		void SetCompressionMethod(int iComp);

		unsigned int GetData(int iFoil, int iTimechannel, int iX, int iY) const;
		unsigned int GetData(int iImage, int iX, int iY) const;
		unsigned int* GetRawData(void) const;

		int LoadFile(const char *pcFileName);
		// uiBufLen: Anzahl Ints (nicht Anzahl Bytes)
		int LoadMem(const unsigned int *puiBuf, unsigned int uiBufLen);

		void GetROI(int iStartX, int iEndX, int iStartY, int iEndY, int iFoil, int iTimechannel, TmpImage *pImg) const;
		void GetGraph(int iStartX, int iEndX, int iStartY, int iEndY, int iFoil, TmpGraph* pGraph) const;
		void GetTotalGraph(int iStartX, int iEndX, int iStartY, int iEndY, double dPhaseShift ,TmpGraph* pGraph) const;
		void GetOverview(TmpImage *pImg) const;
		void GetPhaseGraph(int iFoil, TmpImage *pImg, int iStartX, int iEndX, int iStartY, int iEndY, bool bInDeg=true) const;
		void GetPhaseGraph(int iFoil, TmpImage *pImg, bool bInDeg=true) const;
		void GetContrastGraph(int iFoil, TmpImage *pImg, int iStartX, int iEndX, int iStartY, int iEndY) const;
		void GetContrastGraph(int iFoil, TmpImage *pImg) const;

		void AddFoils(int iBits, int iChannelBits/*=0xffffffff*/, TmpImage *pImg) const;
		void AddFoils(const bool *pbChannels, TmpImage *pImg) const;
		void AddPhases(const bool *pbFoils, TmpImage *pImg) const;
		void AddContrasts(const bool *pbFoils, TmpImage *pImg) const;

		unsigned int GetCounts() const;
		unsigned int GetCounts(int iStartX, int iEndX, int iStartY, int iEndY) const;

		/////////////////////////////////////////////////////////////////
		// alternativer Funktionsaufruf mit Rückgabe des entsprechenden Ergebnisses (für Python-Binding)
		TmpImage GetROI(int iStartX, int iEndX, int iStartY, int iEndY, int iFoil, int iTimechannel) const;
		TmpGraph GetGraph(int iStartX, int iEndX, int iStartY, int iEndY, int iFoil) const;
		TmpGraph GetTotalGraph(int iStartX, int iEndX, int iStartY, int iEndY, double dPhaseShift) const;
		TmpImage GetOverview() const;
		TmpImage GetPhaseGraph(int iFoil, int iStartX, int iEndX, int iStartY, int iEndY, bool bInDeg=true) const;
		TmpImage GetContrastGraph(int iFoil, int iStartX, int iEndX, int iStartY, int iEndY) const;
		TmpImage AddFoils(const bool *pbChannels) const;
		TmpImage AddPhases(const bool *pbFoils) const;
		TmpImage AddContrasts(const bool *pbFoils) const;
		/////////////////////////////////////////////////////////////////
};

#endif
