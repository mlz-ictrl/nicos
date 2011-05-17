//
// global configuration of TOF file layout
//
class Config_TofLoader
{
%TypeHeaderCode
#include "../../tofloader.h"
%End
	public:
		static int GetFoilCount();
		static int GetImagesPerFoil();
		static int GetImageWidth();
		static int GetImageHeight();
		static int GetImageCount();
		static int GetFoilBegin(int iFoil);
		static bool GetPseudoCompression();
		

		static void SetFoilCount(int iNumFoils);		// number of foils in TOF (e.g. 4)
		static void SetImagesPerFoil(int iNumImagesPerFoil);	// number of time channels per foil (e.g. 16)
		static void SetImageWidth(int iImgWidth);		// x_res (e.g. 128)
		static void SetImageHeight(int iImgHeight);		// y_res (e.g. 128)
		static void SetImageCount(int iImgCount);		// total number of images in TOF == t_res (e.g. 128)
		static void SetFoilBegin(int iFoil, int iOffs);		// index of first time channel for each foil (e.g. 0,0;  1, 16;  2, 32;  3, 48)

									// false: all images specified in t_res are sent by server, including padding ones;
		static void SetPseudoCompression(bool bSet);		//        counts in first time are split between first and last channels
									// true: the opposite of both points
		
		static void SetLogLevel(int iLevel);			// Log Level: 0: log nothing, 
									//            1: log errors,
									//            2: log errors & warnings,
									//            3: log errors & warnings & infos
};


/////////////////////////////////////////////////////////////////////////////////////
//
// PAD images
//
class PadImage
{
%TypeHeaderCode
#include "../../tofloader.h"
%End
	public:
		PadImage(const char *pcFileName=NULL, bool bExternalMem=false);
		PadImage(const PadImage& pad);
		virtual ~PadImage();
		
		void SetExternalMem(void* pvDaten);
		int GetPadSize() const;
		int LoadFile(const char *pcFileName);

		// uiBufLen specifies number of ints (NOT # of bytes; unlike CascadeWidget::LoadPadMem)
		int LoadMem(const unsigned int *puiBuf, unsigned int uiBufLen);
		
		void UpdateRange();

		void Print(const char* pcOutFile=NULL);

		unsigned int GetData(int iX, int iY) const;

		unsigned int GetCounts() const;
		unsigned int GetCounts(int iStartX, int iEndX, int iStartY, int iEndY) const;
};

//
// management of temporary images
//
class TmpImage
{
%TypeHeaderCode
#include "../../tofloader.h"
%End
	public:
		TmpImage();
		TmpImage(const TmpImage& tmp);
		virtual ~TmpImage();
		
		void Clear();
		double GetData(int iX, int iY) const;
		unsigned int GetIntData(int iX, int iY) const;
		
		int GetWidth() const;
		int GetHeight() const;
		
		void UpdateRange();
		bool WriteXML(const char* pcFileName) const;
		void ConvertPAD(PadImage* pPad);
		
		void Add(const TmpImage& tmp);
};

//
// management of temporary graphs
//
class TmpGraph
{
%TypeHeaderCode
#include "../../tofloader.h"
%End
	public:
		TmpGraph();
		virtual ~TmpGraph();
		
		bool FitSinus(double &dPhase, double &dScale, double &dAmp, double &dOffs) const;
		
		unsigned int GetData(int iX) const;
		int GetWidth() const;
		int GetMin() const;
		int GetMax() const;
};

//
// TOF images
//
class TofImage
{
%TypeHeaderCode
#include "../../tofloader.h"
%End
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
		
		int LoadFile(const char *pcFileName);

		// uiBufLen specifies number of ints (NOT # of bytes; unlike CascadeWidget::LoadTofMem)
		int LoadMem(const unsigned int *puiBuf, unsigned int uiBufLen);
		
		unsigned int GetCounts() const;
		unsigned int GetCounts(int iStartX, int iEndX, int iStartY, int iEndY) const;				
	
		TmpImage GetROI(int iStartX, int iEndX, int iStartY, int iEndY, int iFoil, int iTimechannel) const;
		TmpGraph GetGraph(int iStartX, int iEndX, int iStartY, int iEndY, int iFoil) const;
		TmpGraph GetTotalGraph(int iStartX, int iEndX, int iStartY, int iEndY, double dPhaseShift) const;
		TmpImage GetOverview() const;
		TmpImage GetPhaseGraph(int iFoil, int iStartX, int iEndX, int iStartY, int iEndY, bool bInDeg=true) const;
		TmpImage GetContrastGraph(int iFoil, int iStartX, int iEndX, int iStartY, int iEndY) const;
		TmpImage AddFoils(const bool *pbChannels) const;
		TmpImage AddPhases(const bool *pbFoils) const;
		TmpImage AddContrasts(const bool *pbFoils) const;
};
/////////////////////////////////////////////////////////////////////////////////////
