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
		PadImage(const char *pcFileName=NULL,
				 bool bExternalMem=false,
				 const PadConfig* conf=0);
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

		const PadConfig& GetPadConfig() const;
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
		TofImage(const char *pcFileName=NULL,
				int iCompression=TOF_COMPRESSION_USEGLOBCONFIG,
				bool bExternalMem=false,
				const TofConfig* conf=0);
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

		const TofConfig& GetTofConfig() const;
};
/////////////////////////////////////////////////////////////////////////////////////
