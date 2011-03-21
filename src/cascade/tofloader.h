// Klassen zum Laden und Verarbeiten von Tof- & Pad-Dateien

#ifndef __TOFLOADER__
#define __TOFLOADER__

// Soll es ein IGOR-Plugin werden?
//#define IGOR_PLUGIN

// Minuit für Fits benutzen?
#define USE_MINUIT

#ifndef NULL
	#define NULL	0
#endif

struct Config_TofLoader
{
	static int FOLIENANZAHL;

	// wieviele Zeitkanaele pro Folie?
	static int BILDERPROFOLIE;

	static int BILDBREITE;
	static int BILDHOEHE;
	static int BILDANZAHL;

	// Folienbeginn
	static int *piFolieBegin;
	
	static int iPhaseBlockSize[2];
	static int iContrastBlockSize[2];
	
	static double LOG_LOWER_RANGE;
	
	static void Init();
	static void Deinit();
	
	// iLen in Ints, nicht Bytes
	static bool GuessConfigFromSize(int iLen, bool bIsTof, bool bFirstCall=true);
};

class TmpImage;
class TofImage;

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
		bool CheckArguments(int iStartX, int iEndX, int iStartY, int iEndY, int iFolie=0, int iZ=0);

	protected:
		unsigned int *m_puiDaten;
		
	public:
		TofImage(const char *pcFileName=NULL);
		virtual ~TofImage();
		
		void Clear(void);
		unsigned int& GetData(int iBild, int iX, int iY);
		unsigned int* GetRawData(void) const;
		
		int LoadFile(const char *pcFileName);
		// uiBufLen: Anzahl Ints (nicht Anzahl Bytes)
		int LoadMem(const unsigned int *puiBuf, unsigned int uiBufLen);
	
		void GetROI(int iStartX, int iEndX, int iStartY, int iEndY, int iFolie, int iZ, const char* pcBaseName="wave", TmpImage *pImg=NULL);
		void GetGraph(int iStartX, int iEndX, int iStartY, int iEndY, int iFolie, const char* pcBaseName="wave", TmpGraph* pGraph=NULL);
		void GetTotalGraph(int iStartX, int iEndX, int iStartY, int iEndY, double dPhaseShift ,const char* pcBaseName="wave", TmpGraph* pGraph=NULL);
		void AddFolien(int iBits, int iZeitKanaeleBits=0xffffffff, const char* pcBaseName="wave", TmpImage *pImg=NULL);
		void AddFolien(const bool *pbKanaele, const char* pcBaseName="wave", TmpImage *pImg=NULL);
		void AddPhases(const bool *pbFolien, const char* pcBaseName="wave", TmpImage *pImg=NULL);
		void AddContrasts(const bool *pbFolien, const char* pcBaseName="wave", TmpImage *pImg=NULL);
		void GetOverview(TmpImage *pImg=NULL);
		void GetPhaseGraph(int iFolie, TmpImage *pImg, int iStartX=-1, int iEndX=-1, int iStartY=-1, int iEndY=-1, bool bInDeg=true);
		void GetContrastGraph(int iFolie, TmpImage *pImg);
};

#endif
