// Cascade-Unterdialoge

#include "graphdlg.h"
#include "sumdialog.h"
#include "calibrationdlg.h"
#include "serverdlg.h"
#include "servercfgdlg.h"

class MainWindow;

// ************************* Kalibrierungs-Dialog *********************
class CalibrationDlg : public QDialog, public Ui::CalibrationDlg
{
	Q_OBJECT
	
	protected:
		QwtPlotGrid *m_pgrid;
		HistogramItem *m_phistogram;
		
	protected slots:
		
	public:
		CalibrationDlg(QWidget *pParent, const Bins& bins) : QDialog(pParent), m_pgrid(0)
		{
			setupUi(this);
			qwtPlot->setCanvasBackground(QColor(Qt::white));
			
			const QwtArray<QwtDoubleInterval>& intervals = bins.GetIntervals();
			const QwtArray<double>& values = bins.GetValues();
			
			m_pgrid = new QwtPlotGrid;
			m_pgrid->enableXMin(true);
			m_pgrid->enableYMin(true);
			m_pgrid->setMajPen(QPen(Qt::black, 0, Qt::DotLine));
			m_pgrid->setMinPen(QPen(Qt::gray, 0 , Qt::DotLine));
			m_pgrid->attach(qwtPlot);
			
			m_phistogram = new HistogramItem();
			m_phistogram->setColor(Qt::black);
			m_phistogram->attach(qwtPlot);
			
			qwtPlot->setAxisScale(QwtPlot::xBottom, 0., 360.);
			qwtPlot->setAxisScale(QwtPlot::yLeft, 0.0, bins.GetMaxVal());
			qwtPlot->axisWidget(QwtPlot::xBottom)->setTitle("Phase [DEG]");
			qwtPlot->axisWidget(QwtPlot::yLeft)->setTitle("Number");
			
			m_phistogram->setData(QwtIntervalData(intervals, values));
			qwtPlot->replot();
		}
		
		virtual ~CalibrationDlg()
		{
			if(m_pgrid) delete m_pgrid;
		}
};
// ********************************************************************




// ************************* Summierungs-Dialog mit Zeitkanälen ***********************
class FolienSummeDlg : public QDialog, public Ui::FolienSummeDlg
{
	Q_OBJECT
	
	protected:
		QTreeWidgetItem** m_pTreeItemsFolien;
		QTreeWidgetItem** m_pTreeItems;
		TofImage *m_pTof;
		MainWindow *m_pParent;
		void (MainWindow::*m_pCallback)(bool*, int);
		int m_iMode;
		
	protected slots:
		void ShowIt()
		{
			bool *pbChecked = new bool[Config_TofLoader::FOLIENANZAHL*Config_TofLoader::BILDERPROFOLIE];
			for(int iFolie=0; iFolie<Config_TofLoader::FOLIENANZAHL; ++iFolie)
			{
				for(int iKanal=0; iKanal<Config_TofLoader::BILDERPROFOLIE; ++iKanal)
				{
					bool bChecked = (m_pTreeItems[iFolie*Config_TofLoader::BILDERPROFOLIE + iKanal]->checkState(0)==Qt::Checked);
					pbChecked[iFolie*Config_TofLoader::BILDERPROFOLIE + iKanal] = bChecked;
				}
			}
			(m_pParent->*m_pCallback)(pbChecked, m_iMode);
			delete[] pbChecked;
		}
		
		void SelectAll()
		{
			for(int iFolie=0; iFolie<Config_TofLoader::FOLIENANZAHL; ++iFolie)
			{
				m_pTreeItemsFolien[iFolie]->setCheckState(0,Qt::Checked);
				for(int iKanal=0; iKanal<Config_TofLoader::BILDERPROFOLIE; ++iKanal)
					m_pTreeItems[iFolie*Config_TofLoader::BILDERPROFOLIE + iKanal]->setCheckState(0,Qt::Checked);
			}
		}
		
		void SelectNone()
		{
			for(int iFolie=0; iFolie<Config_TofLoader::FOLIENANZAHL; ++iFolie)
			{
				m_pTreeItemsFolien[iFolie]->setCheckState(0,Qt::Unchecked);
				for(int iKanal=0; iKanal<Config_TofLoader::BILDERPROFOLIE; ++iKanal)
					m_pTreeItems[iFolie*Config_TofLoader::BILDERPROFOLIE + iKanal]->setCheckState(0,Qt::Unchecked);
			}
		}
		
		void TreeWidgetClicked(QTreeWidgetItem *item, int column)
		{
			int iFolie;
			for(iFolie=0; iFolie<Config_TofLoader::FOLIENANZAHL; ++iFolie)
				if(m_pTreeItemsFolien[iFolie]==item) break;
			if(iFolie==Config_TofLoader::FOLIENANZAHL) return;	// nicht auf Parent geklickt
			
			for(int iKanal=0; iKanal<Config_TofLoader::BILDERPROFOLIE; ++iKanal)
				m_pTreeItems[iFolie*Config_TofLoader::BILDERPROFOLIE + iKanal]->setCheckState(0,m_pTreeItemsFolien[iFolie]->checkState(0));
		}
		
	public:
		FolienSummeDlg(QWidget *pParent, void (MainWindow::*pCallback)(bool*, int)) : QDialog(pParent), m_pCallback(pCallback)
		{
			m_pParent = (MainWindow*)pParent;
			setupUi(this);
			
			m_pTreeItemsFolien = new QTreeWidgetItem*[Config_TofLoader::FOLIENANZAHL];
			m_pTreeItems = new QTreeWidgetItem*[Config_TofLoader::FOLIENANZAHL*Config_TofLoader::BILDERPROFOLIE];

			for(int iFolie=0; iFolie<Config_TofLoader::FOLIENANZAHL; ++iFolie)
			{
				m_pTreeItemsFolien[iFolie] = new QTreeWidgetItem(treeWidget);
				char pcName[256];
				sprintf(pcName, "Foil %d", iFolie+1);
				m_pTreeItemsFolien[iFolie]->setText(0, pcName);
				m_pTreeItemsFolien[iFolie]->setCheckState(0, Qt::Unchecked);
				
				for(int iKanal=0; iKanal<Config_TofLoader::BILDERPROFOLIE; ++iKanal)
				{
					m_pTreeItems[iFolie*Config_TofLoader::BILDERPROFOLIE + iKanal] = new QTreeWidgetItem(m_pTreeItemsFolien[iFolie]);
					m_pTreeItems[iFolie*Config_TofLoader::BILDERPROFOLIE + iKanal]->setCheckState(0, Qt::Unchecked);
					sprintf(pcName, "Time Channel %d", iKanal+1);
					m_pTreeItems[iFolie*Config_TofLoader::BILDERPROFOLIE + iKanal]->setText(0, pcName);
				}
			}
			
			connect(treeWidget, SIGNAL(itemClicked(QTreeWidgetItem *, int)), this, SLOT(TreeWidgetClicked(QTreeWidgetItem *, int)));
			connect(pushButtonShow, SIGNAL(clicked()), this, SLOT(ShowIt()));
			connect(pushButtonSelectAll, SIGNAL(clicked()), this, SLOT(SelectAll()));
			connect(pushButtonSelectNone, SIGNAL(clicked()), this, SLOT(SelectNone()));
		}
		
		virtual ~FolienSummeDlg()
		{
			delete[] m_pTreeItemsFolien; m_pTreeItemsFolien = 0;
			delete[] m_pTreeItems; m_pTreeItems = 0;
		}
		
		void SetMode(int iMode) { m_iMode = iMode; }
};
// ********************************************************************


// ************************* Summierungs-Dialog ohne Zeitkanäle ***********************
class FolienSummeDlgOhneKanaele : public QDialog, public Ui::FolienSummeDlg
{
	Q_OBJECT
	
	protected:
		QTreeWidgetItem** m_pTreeItemsFolien;
		TofImage *m_pTof;
		MainWindow *m_pParent;
		void (MainWindow::*m_pCallback)(bool*, int);
		int m_iMode;
		
	protected slots:
		void ShowIt()
		{
			bool *pbChecked = new bool[Config_TofLoader::FOLIENANZAHL];
			for(int iFolie=0; iFolie<Config_TofLoader::FOLIENANZAHL; ++iFolie)
			{
				bool bChecked = (m_pTreeItemsFolien[iFolie]->checkState(0)==Qt::Checked);
				pbChecked[iFolie] = bChecked;
			}
			(m_pParent->*m_pCallback)(pbChecked, m_iMode);
			delete[] pbChecked;
		}
		
		void SelectAll()
		{
			for(int iFolie=0; iFolie<Config_TofLoader::FOLIENANZAHL; ++iFolie)
				m_pTreeItemsFolien[iFolie]->setCheckState(0,Qt::Checked);
		}
		
		void SelectNone()
		{
			for(int iFolie=0; iFolie<Config_TofLoader::FOLIENANZAHL; ++iFolie)
				m_pTreeItemsFolien[iFolie]->setCheckState(0,Qt::Unchecked);
		}
				
	public:
		FolienSummeDlgOhneKanaele(QWidget *pParent, void (MainWindow::*pCallback)(bool*, int)) : QDialog(pParent), m_pCallback(pCallback)
		{
			m_pParent = (MainWindow*)pParent;
			setupUi(this);
			
			m_pTreeItemsFolien = new QTreeWidgetItem*[Config_TofLoader::FOLIENANZAHL];

			for(int iFolie=0; iFolie<Config_TofLoader::FOLIENANZAHL; ++iFolie)
			{
				m_pTreeItemsFolien[iFolie] = new QTreeWidgetItem(treeWidget);
				char pcName[256];
				sprintf(pcName, "Foil %d", iFolie+1);
				m_pTreeItemsFolien[iFolie]->setText(0, pcName);
				m_pTreeItemsFolien[iFolie]->setCheckState(0, Qt::Unchecked);
			}
			
			connect(pushButtonShow, SIGNAL(clicked()), this, SLOT(ShowIt()));
			connect(pushButtonSelectAll, SIGNAL(clicked()), this, SLOT(SelectAll()));
			connect(pushButtonSelectNone, SIGNAL(clicked()), this, SLOT(SelectNone()));
		}
		
		virtual ~FolienSummeDlgOhneKanaele()
		{
			delete[] m_pTreeItemsFolien; m_pTreeItemsFolien = 0;
		}
		
		void SetMode(int iMode) { m_iMode = iMode; }
};
// ********************************************************************



// ************************* Zeug für Graph-Dialog ***********************
class GraphDlg : public QDialog, public Ui::GraphDlg
{
	Q_OBJECT
	
	protected:
		TofImage *m_pTofImg;
		ErrorBarPlotCurve m_curve;
		QwtPlotCurve m_curvefit, m_curvetotal;
		QwtLegend *m_plegend;
		QwtPlotGrid *m_pgrid;
		
		void UpdateGraph(void)
		{
			// Messpunkte für eine Folie
			TmpGraph tmpGraph;
			m_pTofImg->GetGraph(spinBoxROIx1->value(),spinBoxROIx2->value(),spinBoxROIy1->value(),spinBoxROIy2->value(),spinBoxFolie->value()-1, NULL, &tmpGraph);
			
			double *pdx = new double[tmpGraph.GetWidth()];
			double *pdy = new double[tmpGraph.GetWidth()];
			for(int i=0; i<tmpGraph.GetWidth(); ++i)
			{
				pdx[i]=i;
				pdy[i]=tmpGraph.GetData(i);
			}
			m_curve.setData(pdx,pdy,tmpGraph.GetWidth());
			delete[] pdx;
			delete[] pdy;
			
			
			// Fit dieser Messpunkte
			double dPhase, dFreq, dAmp, dOffs;
			bool bFitValid = tmpGraph.FitSinus(dPhase, dFreq, dAmp, dOffs);
			
			char pcFit[256];
			if(bFitValid)
				sprintf(pcFit, "Fit: y = %.0f * sin(%.4f*x + %.4f) + %.0f", dAmp, dFreq, dPhase, dOffs);
			else 
				sprintf(pcFit, "Fit: invalid!");
			labelFit->setText(pcFit);

			const int FITPUNKTE=16;
			pdx = new double[Config_TofLoader::BILDERPROFOLIE*FITPUNKTE];
			pdy = new double[Config_TofLoader::BILDERPROFOLIE*FITPUNKTE];
			for(int i=0; i<Config_TofLoader::BILDERPROFOLIE*FITPUNKTE; ++i)
			{
				double x = double(i)/double(FITPUNKTE);
				pdx[i] = x;
				pdy[i] = dAmp*sin(x*dFreq + dPhase) + dOffs;
			}
			m_curvefit.setData(pdx,pdy,Config_TofLoader::BILDERPROFOLIE*FITPUNKTE);
			delete[] pdx;
			delete[] pdy;
			
			
			// Gesamtkurve
			TmpGraph tmpGraphtotal;
			m_pTofImg->GetTotalGraph(spinBoxROIx1->value(),spinBoxROIx2->value(),spinBoxROIy1->value(),spinBoxROIy2->value(),spinBoxPhase->value(), NULL, &tmpGraphtotal);
			pdx = new double[tmpGraphtotal.GetWidth()];
			pdy = new double[tmpGraphtotal.GetWidth()];
			for(int i=0; i<tmpGraphtotal.GetWidth(); ++i)
			{
				pdx[i]=i;
				pdy[i]=tmpGraphtotal.GetData(i);
			}
			m_curvetotal.setData(pdx,pdy,tmpGraphtotal.GetWidth());
			delete[] pdx;
			delete[] pdy;

			
			qwtPlot->replot();
		}
		
	protected slots:
		void ROIy1changed(int iVal) { UpdateGraph(); }
		void ROIy2changed(int iVal) { UpdateGraph(); }
		void ROIx1changed(int iVal) { UpdateGraph(); }
		void ROIx2changed(int iVal) { UpdateGraph(); }
		void Foliechanged(int iVal) { UpdateGraph(); }
		void Phasechanged(double dVal) { UpdateGraph(); }
		
	public:
		GraphDlg(QWidget *pParent, TofImage* pTof, int iROIx1, int iROIx2, int iROIy1, int iROIy2, int iFolie) : QDialog(pParent), m_curve("Foil"), m_curvefit("Fit"), m_curvetotal("Total"), m_plegend(0), m_pgrid(0)
		{
			m_pTofImg = pTof;
			setupUi(this);
			
			qwtPlot->setAutoReplot(false);
			qwtPlot->setCanvasBackground(QColor(255,255,255));
			qwtPlot->axisWidget(QwtPlot::xBottom)->setTitle("Time Channels");
			qwtPlot->axisWidget(QwtPlot::yLeft)->setTitle("Counts");
			
			m_pgrid = new QwtPlotGrid;
			m_pgrid->enableXMin(true);
			m_pgrid->enableYMin(true);
			m_pgrid->setMajPen(QPen(Qt::black, 0, Qt::DotLine));
			m_pgrid->setMinPen(QPen(Qt::gray, 0 , Qt::DotLine));
			m_pgrid->attach(qwtPlot);			
			
			spinBoxROIx1->setMinimum(0);
			spinBoxROIx1->setMaximum(Config_TofLoader::BILDBREITE-1);
			spinBoxROIx2->setMinimum(0);
			spinBoxROIx2->setMaximum(Config_TofLoader::BILDBREITE-1);
			spinBoxROIy1->setMinimum(0);
			spinBoxROIy1->setMaximum(Config_TofLoader::BILDHOEHE-1);
			spinBoxROIy2->setMinimum(0);
			spinBoxROIy2->setMaximum(Config_TofLoader::BILDHOEHE-1);
			spinBoxFolie->setMinimum(1);
			spinBoxFolie->setMaximum(Config_TofLoader::FOLIENANZAHL);
			
			spinBoxROIx1->setValue(iROIx1);
			spinBoxROIx2->setValue(iROIx2);
			spinBoxROIy1->setValue(iROIy1);
			spinBoxROIy2->setValue(iROIy2);
			spinBoxFolie->setValue(iFolie+1);
			
			QwtLegend *m_plegend = new QwtLegend;
			//m_plegend->setItemMode(QwtLegend::CheckableItem);
			qwtPlot->insertLegend(m_plegend, QwtPlot::RightLegend);
			
			QObject::connect(spinBoxROIy1, SIGNAL(valueChanged(int)), this, SLOT(ROIy1changed(int)));
			QObject::connect(spinBoxROIy2, SIGNAL(valueChanged(int)), this, SLOT(ROIy2changed(int)));
			QObject::connect(spinBoxROIx1, SIGNAL(valueChanged(int)), this, SLOT(ROIx1changed(int)));
			QObject::connect(spinBoxROIx2, SIGNAL(valueChanged(int)), this, SLOT(ROIx2changed(int)));
			QObject::connect(spinBoxFolie, SIGNAL(valueChanged(int)), this, SLOT(Foliechanged(int)));
			QObject::connect(spinBoxPhase, SIGNAL(valueChanged(double)), this, SLOT(Phasechanged(double)));			
			
			
			// Kurve für Messpunkte für eine Folie
			QwtSymbol sym;
			sym.setStyle(QwtSymbol::Ellipse);
			sym.setPen(QColor(Qt::blue));
			sym.setBrush(QColor(Qt::blue));
			sym.setSize(5);
			m_curve.setSymbol(sym);
			m_curve.setStyle(QwtPlotCurve::NoCurve);
			m_curve.setRenderHint(QwtPlotItem::RenderAntialiased);
			m_curve.setPen(QPen(Qt::blue));
			m_curve.attach(qwtPlot);
			
			// Kurve für Fits
			m_curvefit.setRenderHint(QwtPlotItem::RenderAntialiased);
			QPen penfit = QPen(Qt::red);
			m_curvefit.setPen(penfit);
			m_curvefit.attach(qwtPlot);
			
			// Gesamtkurve
			m_curvetotal.setRenderHint(QwtPlotItem::RenderAntialiased);
			QPen pentotal = QPen(Qt::black);
			pentotal.setWidth(2);
			m_curvetotal.setPen(pentotal);
			m_curvetotal.attach(qwtPlot);
			
			
			UpdateGraph();
		}
		
		virtual ~GraphDlg()
		{
			if(m_pgrid) delete m_pgrid;
			if(m_plegend) delete m_plegend;
		}
};
// **************************************************************

// ************************* Server-Dialog ********************************
class ServerDlg : public QDialog, public Ui::dialogServer
{
	Q_OBJECT
	
	protected:
		
	protected slots:
		
	public:
		ServerDlg(QWidget *pParent) : QDialog(pParent)
		{
			setupUi(this);
		}
		
		virtual ~ServerDlg()
		{
		}
};
// ********************************************************************

// ************************* Server-Dialog ********************************
class ServerCfgDlg : public QDialog, public Ui::ServerConfigDlg
{
	Q_OBJECT
	
	protected:
		static double s_dLastTime;
		
	protected slots:
		
	public:
		ServerCfgDlg(QWidget *pParent) : QDialog(pParent)
		{
			setupUi(this);
			QString str; 
			str.setNum(s_dLastTime);
			editMeasTime->setText(str);
		}
		
		virtual ~ServerCfgDlg()
		{}
		
		double GetMeasTime()
		{
			s_dLastTime = editMeasTime->text().toDouble();
			return s_dLastTime;
		}
};

double ServerCfgDlg::s_dLastTime = 10.0;
// ********************************************************************

#ifdef __CASCADE_QT_CLIENT__
	// Qt-Metaobjekte
	#include "cascadedialoge.moc"
#endif
