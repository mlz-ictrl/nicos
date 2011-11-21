%Module cascadewidget 0

%Import QtGui/QtGuimod.sip
%Import QtCore/QtCoremod.sip
%Import Qwt5/QwtModule.sip

%Include globals.sip
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
		GraphDlg(QWidget *pParent, TofImage* pTof, int iFoil);
		virtual ~GraphDlg();
};
/////////////////////////////////////////////////////////////////////////////////////


class MainRasterData : QwtRasterData
{
%TypeHeaderCode
#include "../../tofdata.h"
%End

	public:
		MainRasterData(const QwtDoubleRect& rect);
		MainRasterData();
		MainRasterData(const MainRasterData& data2d);
		virtual ~MainRasterData();

		void SetLog10(bool bLog10);
		bool GetLog10() const;

		void SetImage(BasicImage** pImg);
		BasicImage* GetImage();

		void SetPhaseData(bool bPhaseData);	// wegen Achsen-Range
		void clearData();

		virtual QwtRasterData *copy() const;
		virtual QwtDoubleInterval range() const;
		virtual double value(double x, double y) const;

		// get (nonlog) raw value without regard to m_bLog
		double GetValueRaw(int x, int y) const;

		int GetWidth() const;
		int GetHeight() const;

		void SetAutoCountRange(bool bAuto);
		void SetCountRange(double dMin, double dMax);
};


/////////////////////////////////////////////////////////////////////////////////////

class Plot : QwtPlot
{
%TypeHeaderCode
#include "../../cascadewidget.h"
%End
	public:
		void ChangeRange();
		void ChangeRange_xy();

		QwtPlotZoomer* GetZoomer();
		QwtPlotPanner* GetPanner();

		void SetData(MainRasterData* pData, bool bUpdate=true);
		const QwtRasterData* GetData() const;

		void SetColorMap(bool bCyclic);
		Plot(QWidget *parent);

	public slots:
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
		// use the GlobalConfig setter methods to configure
		// layout of TOF file before calling LoadTofMem / LoadTofFile
		// otherwise default or guessed layout will be assumed
		//
		bool LoadPadFile(const char* pcFile);			// load PAD from file
		bool LoadTofFile(const char* pcFile);			// load TOF from file
		bool LoadPadMem(const char* pcMem, unsigned int iLen);	// load PAD from mem
		bool LoadTofMem(const char* pcMem, unsigned int iLen);	// load TOF from mem

		// get total counts of currently loaded PAD or TOF
		unsigned int GetCounts() const;

		// loading/saving of ROI elements
		bool LoadRoi(const char* pcFile);
		bool SaveRoi(const char* pcFile);

		TofImage* GetTof();
		TmpImage* GetTmpImg();
		MainRasterData& GetData2d();
		PadImage* GetPad();
		Plot* GetPlot();

		bool GetLog10();
		int GetFoil() const;
		int GetTimechannel() const;

		void SetMode(int iMode);
		int GetMode();

		void SetRoiDrawMode(int iMode);

		bool IsRoiInUse();
		void UseRoi(bool bUse);

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
		void showRoiDlg();
		void showBrowseDlg(const char* pcDir=".");
		/////////////////////////////////////////////

		void SetLog10(bool bLog10);
		void SetFoil(int iFolie);
		void SetTimechannel(int iKanal);

		void UpdateGraph();
		void UpdateLabels();
		void UpdateRange();
};
