%Module cascadewidget 0

%Import QtGui/QtGuimod.sip
%Import QtCore/QtCoremod.sip
%Import Qwt5/QwtModule.sip


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

		bool LoadPadFile(const char* pcFile);			// PAD aus Datei laden
		bool LoadTofFile(const char* pcFile);			// TOF aus Datei laden
		bool LoadPadMem(const char* pcMem, unsigned int iLen);	// PAD aus Speicher laden
		bool LoadTofMem(const char* pcMem, unsigned int iLen);	// TOF aus Speicher laden

//		TofImage* GetTof();
//		Data2D* GetData2d();
//		PadData* GetPad();
		Plot* GetPlot();
//		unsigned int* GetRawData();	// Pointer auf Rohdaten-Bereich erhalten
		
		bool GetLog10();
		int GetFolie() const;
		int GetZeitkanal() const;
		
		void SetMode(int iMode);
		int GetMode();

	public slots:
		void viewOverview();		// alle Folien aller Zeitkanaele aufsummieren
		void viewSlides();		// einzelne Folie anzeigen
		void viewPhases();		// Phasen 
		void viewContrasts();		// Kontraste
		
		void viewFoilSums(const bool* pbKanaele);
		void viewPhaseSums(const bool* pbFolien);
		void viewContrastSums(const bool* pbFolien);
		
		void SetLog10(bool bLog10);
		void SetSpectrogram(bool bSpect);
		void SetContour(bool bCont);
		void SetFolie(int iFolie);
		void SetZeitkanal(int iKanal);
		
		void UpdateGraph();
		void UpdateLabels();		
		void UpdateRange();
};

