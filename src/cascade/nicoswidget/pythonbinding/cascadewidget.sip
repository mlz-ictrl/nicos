%Module cascadewidget 0

%Import QtGui/QtGuimod.sip
%Import QtCore/QtCoremod.sip
%Import Qwt5/QwtModule.sip


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
};


/////////////////////////////////////////////////////////////////////////////////////
// GraphDlg
// use CascadeWidget::showGraphDlg() instead
class GraphDlg : QDialog
{
%TypeHeaderCode
#include "../../cascadedialogs.h"
%End
	public:
		GraphDlg(QWidget *pParent, TofImage* pTof);
		GraphDlg(QWidget *pParent, TofImage* pTof, int iROIx1, int iROIx2, int iROIy1, int iROIy2, int iFolie);
		virtual ~GraphDlg();
};
/////////////////////////////////////////////////////////////////////////////////////


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
		PadImage(const char *pcFileName=NULL);
		PadImage(const PadImage& pad);
		virtual ~PadImage();
		
		int LoadFile(const char *pcFileName);

		// uiBufLen specifies number of ints (NOT # of bytes; unlike CascadeWidget::LoadPadMem)
		int LoadMem(const unsigned int *puiBuf, unsigned int uiBufLen);
		
		void UpdateRange();

		void Print(const char* pcOutFile=NULL);

		unsigned int GetData(int iX, int iY) const;
//		unsigned int* GetRawData(void);
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
		
		int GetWidth() const;
		int GetHeight() const;
		
		void UpdateRange();
		bool WriteXML(const char* pcFileName);
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
		
		bool FitSinus(double &dPhase, double &dScale, double &dAmp, double &dOffs);
		
		unsigned int GetData(int iX);
		int GetWidth();
		int GetMin();
		int GetMax();
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
		TofImage(const char *pcFileName=NULL);
		virtual ~TofImage();
		
		void Clear();
		unsigned int GetData(int iFoil, int iTimechannel, int iX, int iY);
//		unsigned int& GetData(int iBild, int iX, int iY);
//		unsigned int* GetRawData(void) const;
		
		int LoadFile(const char *pcFileName);

		// uiBufLen specifies number of ints (NOT # of bytes; unlike CascadeWidget::LoadTofMem)
		int LoadMem(const unsigned int *puiBuf, unsigned int uiBufLen);
	
		TmpImage GetROI(int iStartX, int iEndX, int iStartY, int iEndY, int iFoil, int iTimechannel);
		TmpGraph GetGraph(int iStartX, int iEndX, int iStartY, int iEndY, int iFoil);
		TmpGraph GetTotalGraph(int iStartX, int iEndX, int iStartY, int iEndY, double dPhaseShift);
		TmpImage GetOverview();
		TmpImage GetPhaseGraph(int iFoil, int iStartX, int iEndX, int iStartY, int iEndY, bool bInDeg=true);
		TmpImage GetContrastGraph(int iFoil, int iStartX, int iEndX, int iStartY, int iEndY);
		TmpImage AddFoils(const bool *pbChannels);
		TmpImage AddPhases(const bool *pbFoils);
		TmpImage AddContrasts(const bool *pbFoils);
};
/////////////////////////////////////////////////////////////////////////////////////


class MainRasterData :  QwtRasterData
{
%TypeHeaderCode
#include "../../tofdata.h"
%End
	public:
		MainRasterData(const QwtDoubleRect& rect);
		
		void SetLog10(bool bLog10);
		bool GetLog10() const;
		
		// get raw (nonlog) value independent of m_bLog
		virtual double GetValueRaw(int x, int y) const = 0;
};


// *********************** PAD-Daten *********************** 
class PadData :  MainRasterData, PadImage
{
%TypeHeaderCode
#include "../../tofdata.h"
%End
	public:
		PadData();
		PadData(const PadData& pad);
		virtual ~PadData();

		virtual QwtRasterData *copy() const;
		virtual QwtDoubleInterval range() const;
		virtual double value(double x, double y) const;
		virtual double GetValueRaw(int x, int y) const;
};


// *********************** TOF-Daten ***********************
class Data2D :  MainRasterData, TmpImage
{
%TypeHeaderCode
#include "../../tofdata.h"
%End
	public:
		Data2D(const QwtDoubleRect& rect);
		Data2D();
		Data2D(const Data2D& data2d);
		virtual ~Data2D();
		
		void SetPhaseData(bool bPhaseData);	// due to axis range
		void clearData();
		
		virtual QwtRasterData *copy() const;
		virtual QwtDoubleInterval range() const;
		virtual double value(double x, double y) const;
		virtual double GetValueRaw(int x, int y) const;
};
/////////////////////////////////////////////////////////////////////////////////////

class Plot : QwtPlot
{
%TypeHeaderCode
#include "../../cascadewidget.h"
%End
	public:
		void ChangeRange();
		QwtPlotZoomer* GetZoomer();

		void SetData(QwtRasterData* pData);
		const QwtRasterData* GetData() const;

		void SetColorMap(bool bCyclic);
		Plot(QWidget *parent);

	public slots:
		void showContour(bool on);
		void showSpectrogram(bool on);
		void printPlot();
};


class CascadeWidget : QWidget
{
%TypeHeaderCode
#include "../../cascadewidget.h"
%End

	public:
		CascadeWidget(QWidget *parent=NULL);
		virtual ~CascadeWidget();
		
		void Unload();
		bool IsTofLoaded() const;
		bool IsPadLoaded() const;
		void* NewPad();
		void* NewTof();

		//
		// use the Config_TofLoader setter methods to configure
		// layout of TOF file before calling LoadTofMem / LoadTofFile
		// otherwise default or guessed layout will be assumed
		//
		bool LoadPadFile(const char* pcFile);			// load PAD from file
		bool LoadTofFile(const char* pcFile);			// load TOF from file
		bool LoadPadMem(const char* pcMem, unsigned int iLen);	// load PAD from mem
		bool LoadTofMem(const char* pcMem, unsigned int iLen);	// load TOF from mem

		TofImage* GetTof();
		Data2D* GetData2d();
		PadData* GetPad();
		Plot* GetPlot();
		
		bool GetLog10();
		int GetFoil() const;
		int GetTimechannel() const;
		
		void SetMode(int iMode);
		int GetMode();

	public slots:
		void viewOverview();		// add all time channels of all foils
		void viewSlides();		// show single foils
		void viewPhases();		// show phases
		void viewContrasts();		// show contrasts
		
		void viewFoilSums(const bool* pbKanaele);
		void viewPhaseSums(const bool* pbFolien);
		void viewContrastSums(const bool* pbFolien);

		// sub dialogs //////////////////////////////
		void showCalibrationDlg(int iNumBins);
		void showGraphDlg();
		void showSumDlg();
		/////////////////////////////////////////////
		
		void SetLog10(bool bLog10);
		void SetSpectrogram(bool bSpect);
		void SetContour(bool bCont);
		void SetFoil(int iFolie);
		void SetTimechannel(int iKanal);
		
		void UpdateGraph();
		void UpdateLabels();		
		void UpdateRange();
};
