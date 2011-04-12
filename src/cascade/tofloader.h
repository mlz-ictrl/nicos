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

//#define IGOR_PLUGIN		// Soll es ein IGOR-Plugin werden?
#define USE_MINUIT		// Minuit für Fits benutzen?

#ifndef NULL
	#define NULL	0
#endif

class TmpImage;
class TmpGraph;
class TofImage;
class PadImage;

// Konfiguration
class Config_TofLoader
{
	friend class TmpImage;
	friend class TmpGraph;
	friend class TofImage;
	friend class PadImage;
	
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

	public:
		// iLen in Ints, nicht Bytes
		static bool GuessConfigFromSize(int iLen, bool bIsTof, bool bFirstCall=true);		
		static void Init();
		static void Deinit();
		
		static int GetLogLowerRange();
		static int GetFoilCount();
		static int GetImagesPerFoil();
		static int GetImageWidth();
		static int GetImageHeight();
		static int GetImageCount();
		static int GetFoilBegin(int iFoil);
		
		static void SetFoilCount(int iNumFoils);
		static void SetImagesPerFoil(int iNumImagesPerFoil);
		static void SetImageWidth(int iImgWidth);
		static void SetImageHeight(int iImgHeight);
		static void SetImageCount(int iImgCount);
		static void SetFoilBegin(int iFoil, int iOffs);
};


#define LOAD_SUCCESS		 1
#define LOAD_FAIL		 0
#define LOAD_SIZE_MISMATCH	-1

// PAD-Bilder
class PadImage
{
	friend class TmpImage;
	
	protected:
		unsigned int *m_puiDaten;
		int m_iMin, m_iMax;
		void Clear(void);
	
	public:
		PadImage(const char *pcFileName=NULL);
		PadImage(const PadImage& pad);
		virtual ~PadImage();
		
		int LoadFile(const char *pcFileName);
		// uiBufLen: Anzahl Ints (nicht Anzahl Bytes)
		int LoadMem(const unsigned int *puiBuf, unsigned int uiBufLen);
		
		void UpdateRange();
		
#ifdef IGOR_PLUGIN
		void Print(const char* pcBaseName="wave");
#else
		void Print(const char* pcOutFile=NULL);
#endif

		unsigned int GetData(int iX, int iY) const;
		unsigned int* GetRawData(void);
};

// Klasse, um Zwischenbilder zu verwalten
class TmpImage
{
	friend class PadImage;
	friend class TofImage;
  
  protected:
	int m_iW, m_iH;
	unsigned int* m_puiDaten;	// für Counts-Diagramm
	double* m_pdDaten;		// für Phasen- und Kontrastdiagramm
	double m_dMin, m_dMax;
	
  public:
	TmpImage();
	TmpImage(const TmpImage& tmp);
	virtual ~TmpImage();
	
	void Clear(void);
	
	double GetData(int iX, int iY) const;
	
	int GetWidth() const;
	int GetHeight() const;
	
	void UpdateRange();
	bool WriteXML(const char* pcFileName);
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
	
	bool FitSinus(double &dPhase, double &dScale, double &dAmp, double &dOffs);
	
	unsigned int GetData(int iX);
	int GetWidth(void);
	int GetMin();
	int GetMax();
};

// TOF-Bilder
class TofImage
{
	private:
		void CheckArguments(int* piStartX, int* piEndX, int* piStartY, int* piEndY, int* piFoil=0, int* piTimechannel=0);

	protected:
		unsigned int *m_puiDaten;
		
	public:
		TofImage(const char *pcFileName=NULL);
		virtual ~TofImage();
		
		void Clear(void);
		
		unsigned int GetData(int iFoil, int iTimechannel, int iX, int iY);
		unsigned int& GetData(int iImage, int iX, int iY);
		unsigned int* GetRawData(void) const;
		
		int LoadFile(const char *pcFileName);
		// uiBufLen: Anzahl Ints (nicht Anzahl Bytes)
		int LoadMem(const unsigned int *puiBuf, unsigned int uiBufLen);
	
		void GetROI(int iStartX, int iEndX, int iStartY, int iEndY, int iFoil, int iTimechannel, TmpImage *pImg);
		void GetGraph(int iStartX, int iEndX, int iStartY, int iEndY, int iFoil, TmpGraph* pGraph);
		void GetTotalGraph(int iStartX, int iEndX, int iStartY, int iEndY, double dPhaseShift ,TmpGraph* pGraph);
		void GetOverview(TmpImage *pImg);
		void GetPhaseGraph(int iFoil, TmpImage *pImg, int iStartX, int iEndX, int iStartY, int iEndY, bool bInDeg=true);
		void GetPhaseGraph(int iFoil, TmpImage *pImg, bool bInDeg=true);
		void GetContrastGraph(int iFoil, TmpImage *pImg);		
		
		void AddFoils(int iBits, int iChannelBits/*=0xffffffff*/, TmpImage *pImg);
		void AddFoils(const bool *pbChannels, TmpImage *pImg);
		void AddPhases(const bool *pbFoils, TmpImage *pImg);
		void AddContrasts(const bool *pbFoils, TmpImage *pImg);
		
		/////////////////////////////////////////////////////////////////
		// alternativer Funktionsaufruf mit Rückgabe des entsprechenden Ergebnisses (für Python-Binding)
		TmpImage GetROI(int iStartX, int iEndX, int iStartY, int iEndY, int iFoil, int iTimechannel);
		TmpGraph GetGraph(int iStartX, int iEndX, int iStartY, int iEndY, int iFoil);
		TmpGraph GetTotalGraph(int iStartX, int iEndX, int iStartY, int iEndY, double dPhaseShift);
		TmpImage GetOverview();
		TmpImage GetPhaseGraph(int iFoil, int iStartX, int iEndX, int iStartY, int iEndY, bool bInDeg=true);
		TmpImage GetContrastGraph(int iFoil);
		TmpImage AddFoils(const bool *pbChannels);
		TmpImage AddPhases(const bool *pbFoils);
		TmpImage AddContrasts(const bool *pbFoils);
		/////////////////////////////////////////////////////////////////
};

#endif
