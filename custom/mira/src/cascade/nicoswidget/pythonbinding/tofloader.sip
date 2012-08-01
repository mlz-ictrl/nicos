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

		// strBufLen specifies number of bytes
		int LoadMem(const char *strBuf, unsigned int strBufLen);

		void UpdateRange();

		void Print(const char* pcOutFile=NULL);

		virtual unsigned int GetData(int iX, int iY) const;
		virtual double GetDoubleData(int iX, int iY) const;
		virtual unsigned int GetIntData(int iX, int iY) const;

		// same as above, but return 0 if outside ROI (if ROI is used)
		unsigned int GetDataInsideROI(int iX, int iY) const;

		unsigned int GetCounts() const;
		unsigned int GetCounts(int iStartX, int iEndX,
							   int iStartY, int iEndY) const;

		const PadConfig& GetPadConfig() const;

		virtual int GetIntMin() const;
		virtual int GetIntMax() const;
		virtual double GetDoubleMin() const;
		virtual double GetDoubleMax() const;

		virtual int GetWidth() const;
		virtual int GetHeight() const;
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

		virtual int GetWidth() const;
		virtual int GetHeight() const;

		virtual int GetIntMin() const;
		virtual int GetIntMax() const;
		virtual double GetDoubleMin() const;
		virtual double GetDoubleMax() const;

		void UpdateRange();
		bool WriteXML(const char* pcFileName,
					  int iSampleDetector=0,
					  double iWavelength=0,
					  double iLifetime=0,
					  int iBeamMonitor=0) const;
		void ConvertPAD(PadImage* pPad);

		void Add(const TmpImage& tmp);

		// Gaussian fit for finding the beam center
		bool FitGaussian(double &dAmp,
						 double &dCenterX, double &dCenterY,
						 double &dSpreadX, double &dSpreadY) const;
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
		TmpGraph(const TofConfig* pTofConf=0);
		virtual ~TmpGraph();

		bool FitSinus(double& dFreq, double &dPhase, double &dAmp, double &dOffs,
				double &dPhase_err, double &dAmp_err, double &dOffs_err) const;
		//bool FitSinus(double& dFreq, double &dPhase, double &dAmp, double &dOffs) const;
		
		bool GetContrast(double &dContrast, double &dPhase,
				    double &dContrast_err, double &dPhase_err) const;
		//bool GetContrast(double &dContrast, double &dPhase) const;

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
				bool bExternalMem=false,
				const TofConfig* conf=0);
		virtual ~TofImage();

		void SetExternalMem(void* pvDaten);
		int GetTofSize() const;
		void Clear();

		unsigned int GetData(int iFoil, int iTimechannel, int iX, int iY) const;
		unsigned int GetData(int iImage, int iX, int iY) const;

		// same as above, but return 0 if outside ROI (if ROI is used)
		unsigned int GetDataInsideROI(int iFoil, int iTimechannel,
									  int iX, int iY) const;
		unsigned int GetDataInsideROI(int iImage, int iX, int iY) const;

		int LoadFile(const char *pcFileName);

		// strBufLen specifies number of bytes
		int LoadMem(const char *strBuf, unsigned int strBufLen);

		unsigned int GetCounts() const;
		unsigned int GetCounts(int iStartX, int iEndX,
							   int iStartY, int iEndY) const;

		TmpImage GetROI(int iStartX, int iEndX, int iStartY, int iEndY, int iFoil, int iTimechannel) const;
		TmpGraph GetGraph(int iStartX, int iEndX, int iStartY, int iEndY, int iFoil) const;
		TmpGraph GetGraph(int iFoil) const;
		TmpGraph GetTotalGraph(int iStartX, int iEndX, int iStartY, int iEndY, double dPhaseShift) const;
		TmpImage GetOverview(bool bOnlyInRoi=false) const;
		TmpImage GetPhaseGraph(int iFoil, bool bInDeg=true) const;
		TmpImage GetContrastGraph(int iFoil) const;
		TmpImage AddFoils(const bool *pbChannels) const;
		TmpImage AddPhases(const bool *pbFoils) const;
		TmpImage AddContrasts(const bool *pbFoils) const;

		const TofConfig& GetTofConfig() const;
};
/////////////////////////////////////////////////////////////////////////////////////
