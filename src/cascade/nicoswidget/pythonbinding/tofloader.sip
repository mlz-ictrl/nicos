//
// minimal interface for images
//
class BasicImage
{
%TypeHeaderCode
#include "../../tofloader.h"
%End

	public:
		virtual int GetWidth() const = 0;
		virtual int GetHeight() const = 0;

		virtual double GetDoubleData(int iX, int iY) const = 0;
		virtual unsigned int GetIntData(int iX, int iY) const = 0;

		virtual int GetIntMin() const = 0;
		virtual int GetIntMax() const = 0;
		virtual double GetDoubleMin() const = 0;
		virtual double GetDoubleMax() const = 0;
};

//
// PAD images
//
class PadImage : BasicImage
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
		int SaveFile(const char *pcFileName);

		// uiBufLen specifies number of ints (NOT # of bytes; unlike CascadeWidget::LoadPadMem)
		int LoadMem(const unsigned int *puiBuf, unsigned int uiBufLen);

		void UpdateRange();

		void Print(const char* pcOutFile=NULL);

		virtual unsigned int GetData(int iX, int iY) const;
		virtual double GetDoubleData(int iX, int iY) const;
		virtual unsigned int GetIntData(int iX, int iY) const;

		// same as above, but return 0 if outside ROI (if ROI is used)
		unsigned int GetDataInsideROI(int iX, int iY) const;

		unsigned int GetCounts() const;

		const PadConfig& GetPadConfig() const;
};

//
// management of temporary images
//
class TmpImage : BasicImage
{
%TypeHeaderCode
#include "../../tofloader.h"
%End
	public:
		TmpImage();
		TmpImage(const TmpImage& tmp);
		virtual ~TmpImage();

		void Clear();

		virtual double GetData(int iX, int iY) const;
		virtual unsigned int GetIntData(int iX, int iY) const;
		virtual double GetDoubleData(int iX, int iY) const;

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

		// same as above, but return 0 if outside ROI (if ROI is used)
		unsigned int GetDataInsideROI(int iFoil, int iTimechannel,
									  int iX, int iY) const;
		unsigned int GetDataInsideROI(int iImage, int iX, int iY) const;

		int LoadFile(const char *pcFileName);

		// uiBufLen specifies number of ints (NOT # of bytes; unlike CascadeWidget::LoadTofMem)
		int LoadMem(const unsigned int *puiBuf, unsigned int uiBufLen);

		unsigned int GetCounts() const;

		TmpImage GetROI(int iStartX, int iEndX, int iStartY, int iEndY, int iFoil, int iTimechannel) const;
		TmpGraph GetGraph(int iStartX, int iEndX, int iStartY, int iEndY, int iFoil) const;
		TmpGraph GetGraph(int iFoil) const;
		TmpGraph GetTotalGraph(int iStartX, int iEndX, int iStartY, int iEndY, double dPhaseShift) const;
		TmpImage GetOverview() const;
		TmpImage GetPhaseGraph(int iFoil, bool bInDeg=true) const;
		TmpImage GetContrastGraph(int iFoil) const;
		TmpImage AddFoils(const bool *pbChannels) const;
		TmpImage AddPhases(const bool *pbFoils) const;
		TmpImage AddContrasts(const bool *pbFoils) const;

		const TofConfig& GetTofConfig() const;
};
/////////////////////////////////////////////////////////////////////////////////////
