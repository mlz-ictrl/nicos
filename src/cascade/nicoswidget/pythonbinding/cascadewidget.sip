%Module cascadewidget 0

%Import QtGui/QtGuimod.sip
%Import QtCore/QtCoremod.sip
%Import Qwt5/QwtModule.sip

%Include tofloader.sip


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
		void* NewTof(int iCompression = TOF_COMPRESSION_USEGLOBCONFIG);

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
