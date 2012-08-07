// *****************************************************************************
// NICOS, the Networked Instrument Control System of the FRM-II
// Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
//
// This program is free software; you can redistribute it and/or modify it under
// the terms of the GNU General Public License as published by the Free Software
// Foundation; either version 2 of the License, or (at your option) any later
// version.
//
// This program is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
// FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
// details.
//
// You should have received a copy of the GNU General Public License along with
// this program; if not, write to the Free Software Foundation, Inc.,
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
// Module authors:
//   Tobias Weber <tweber@frm2.tum.de>
//
// *****************************************************************************
// Cascade sub dialogs

// ************************* Kalibrierungs-Dialog *********************
CalibrationDlg::CalibrationDlg(QWidget *pParent, const Bins& bins) :
								QDialog(pParent), m_pgrid(0)
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

CalibrationDlg::~CalibrationDlg()
{
	if(m_pgrid) delete m_pgrid;
}
// *****************************************************************************




// ************************* Summierungs-Dialog mit Zeitkanälen ****************
void SumDlg::ShowIt()
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	bool *pbChecked = new bool[conf.GetFoilCount()*conf.GetImagesPerFoil()];
	for(int iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
	{
		for(int iKanal=0; iKanal<conf.GetImagesPerFoil(); ++iKanal)
		{
			bool bChecked =
				(m_pTreeItems[iFolie*conf.GetImagesPerFoil() +
				iKanal]->checkState(0)==Qt::Checked);
			pbChecked[iFolie*conf.GetImagesPerFoil() + iKanal] = bChecked;
		}
	}
	emit SumSignal(pbChecked, m_iMode);
	delete[] pbChecked;
}

void SumDlg::SelectAll()
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	for(int iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
	{
		m_pTreeItemsFolien[iFolie]->setCheckState(0,Qt::Checked);
		for(int iKanal=0; iKanal<conf.GetImagesPerFoil(); ++iKanal)
			m_pTreeItems[iFolie*conf.GetImagesPerFoil() + iKanal]
												->setCheckState(0,Qt::Checked);
	}
}

void SumDlg::SelectNone()
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	for(int iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
	{
		m_pTreeItemsFolien[iFolie]->setCheckState(0,Qt::Unchecked);
		for(int iKanal=0; iKanal<conf.GetImagesPerFoil(); ++iKanal)
			m_pTreeItems[iFolie*conf.GetImagesPerFoil() + iKanal]
												->setCheckState(0,Qt::Unchecked);
	}
}

void SumDlg::TreeWidgetClicked(QTreeWidgetItem *item, int column)
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	int iFolie;
	for(iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
		if(m_pTreeItemsFolien[iFolie]==item) break;

	// nicht auf Parent geklickt
	if(iFolie==conf.GetFoilCount()) return;

	for(int iKanal=0; iKanal<conf.GetImagesPerFoil(); ++iKanal)
		m_pTreeItems[iFolie*conf.GetImagesPerFoil() + iKanal]
				->setCheckState(0,m_pTreeItemsFolien[iFolie]->checkState(0));
}

SumDlg::SumDlg(QWidget *pParent) : QDialog(pParent)
{
	setupUi(this);

	const TofConfig& conf = GlobalConfig::GetTofConfig();

	m_pTreeItemsFolien = new QTreeWidgetItem*[conf.GetFoilCount()];
	m_pTreeItems = new QTreeWidgetItem*[conf.GetFoilCount()*
										conf.GetImagesPerFoil()];

	for(int iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
	{
		m_pTreeItemsFolien[iFolie] = new QTreeWidgetItem(treeWidget);
		char pcName[256];
		sprintf(pcName, "Foil %d", iFolie+1);
		m_pTreeItemsFolien[iFolie]->setText(0, pcName);
		m_pTreeItemsFolien[iFolie]->setCheckState(0, Qt::Unchecked);

		for(int iKanal=0; iKanal<conf.GetImagesPerFoil(); ++iKanal)
		{
			m_pTreeItems[iFolie*conf.GetImagesPerFoil() + iKanal] =
								new QTreeWidgetItem(m_pTreeItemsFolien[iFolie]);
			m_pTreeItems[iFolie*conf.GetImagesPerFoil() + iKanal]
											->setCheckState(0, Qt::Unchecked);
			sprintf(pcName, "Time Channel %d", iKanal+1);
			m_pTreeItems[iFolie*conf.GetImagesPerFoil() + iKanal]
														->setText(0, pcName);
		}
	}

	connect(treeWidget, SIGNAL(itemClicked(QTreeWidgetItem *, int)), this,
								SLOT(TreeWidgetClicked(QTreeWidgetItem *, int)));
	connect(pushButtonShow, SIGNAL(clicked()), this, SLOT(ShowIt()));
	connect(pushButtonSelectAll, SIGNAL(clicked()), this, SLOT(SelectAll()));
	connect(pushButtonSelectNone, SIGNAL(clicked()), this, SLOT(SelectNone()));
}

SumDlg::~SumDlg()
{
	delete[] m_pTreeItemsFolien; m_pTreeItemsFolien = 0;
	delete[] m_pTreeItems; m_pTreeItems = 0;
}

void SumDlg::SetMode(int iMode) { m_iMode = iMode; }
// *****************************************************************************


// ************************* Summierungs-Dialog ohne Zeitkanäle ****************
void SumDlgNoChannels::ShowIt()
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	bool *pbChecked = new bool[conf.GetFoilCount()];
	for(int iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
	{
		bool bChecked = (m_pTreeItemsFolien[iFolie]->checkState(0)==Qt::Checked);
		pbChecked[iFolie] = bChecked;
	}
	emit SumSignal(pbChecked, m_iMode);
	delete[] pbChecked;
}

void SumDlgNoChannels::SelectAll()
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	for(int iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
		m_pTreeItemsFolien[iFolie]->setCheckState(0,Qt::Checked);
}

void SumDlgNoChannels::SelectNone()
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	for(int iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
		m_pTreeItemsFolien[iFolie]->setCheckState(0,Qt::Unchecked);
}

SumDlgNoChannels::SumDlgNoChannels(QWidget *pParent) : QDialog(pParent)
{
	setupUi(this);

	const TofConfig& conf = GlobalConfig::GetTofConfig();

	m_pTreeItemsFolien = new QTreeWidgetItem*[conf.GetFoilCount()];

	for(int iFolie=0; iFolie<conf.GetFoilCount(); ++iFolie)
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

SumDlgNoChannels::~SumDlgNoChannels()
{
	delete[] m_pTreeItemsFolien; m_pTreeItemsFolien = 0;
}

void SumDlgNoChannels::SetMode(int iMode) { m_iMode = iMode; }
// *****************************************************************************





// ************************* Zeug für Graph-Dialog *****************************
void GraphDlg::UpdateGraph(void)
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

	// Messpunkte für eine Folie
	TmpGraph tmpGraph;
	tmpGraph = m_pTofImg->GetGraph(spinBoxFolie->value()-1);

	double *pdx = new double[tmpGraph.GetWidth()];
	double *pdy = new double[tmpGraph.GetWidth()];
	for(int i=0; i<tmpGraph.GetWidth(); ++i)
	{
		pdx[i]=i;
		pdy[i]=tmpGraph.GetData(i);
	}
	m_curve.setData(pdx,pdy,tmpGraph.GetWidth());

	double dymax = *std::max_element(pdy, pdy+tmpGraph.GetWidth());

	delete[] pdx;
	delete[] pdy;


	if(checkBoxDoFit->isChecked())
	{
		// Fit dieser Messpunkte
		double dFreq, dPhase, dAmp, dOffs;
		double dPhase_err, dAmp_err, dOffs_err;
		bool bFitValid = tmpGraph.FitSinus(dFreq, dPhase, dAmp, dOffs,
											dPhase_err, dAmp_err, dOffs_err);

		double dContrast = dAmp/dOffs;
		double dContrast_err =
			sqrt((1/dOffs*dAmp_err)*(1/dOffs*dAmp_err)
			+ (-dAmp/(dOffs*dOffs)*dOffs_err)*(-dAmp/(dOffs*dOffs)*dOffs_err));

		char pcFit[256];
		if(bFitValid)
		{
			sprintf(pcFit, "Contrast: %g +- %g\nPhase: %g +- %g",
							dContrast, dContrast_err,
							dPhase, dPhase_err);
		}
		else
		{
			sprintf(pcFit, "Fit: invalid!");
			dAmp = dFreq = dPhase = dOffs = 0.;
		}

		labelFit->setText(pcFit);

		const int FITPUNKTE=16;
		pdx = new double[conf.GetImagesPerFoil()*FITPUNKTE];
		pdy = new double[conf.GetImagesPerFoil()*FITPUNKTE];
		for(int i=0; i<conf.GetImagesPerFoil()*FITPUNKTE; ++i)
		{
			double x = double(i)/double(FITPUNKTE);
			pdx[i] = x;
			pdy[i] = dAmp*sin(x*dFreq + dPhase) + dOffs;
		}
		m_curvefit.setData(pdx, pdy, conf.GetImagesPerFoil()*FITPUNKTE);
		delete[] pdx;
		delete[] pdy;
	}
	else
	{
		m_curvefit.setData(0,0,0);
	}

	/*
	// Gesamtkurve
	TmpGraph tmpGraphtotal;
	m_pTofImg->GetTotalGraph(spinBoxROIx1->value(),spinBoxROIx2->value(),
		spinBoxROIy1->value(),spinBoxROIy2->value(),spinBoxPhase->value(),
		&tmpGraphtotal);
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
	*/

	qwtPlot->setAxisScale(QwtPlot::yLeft, 0., dymax);
	qwtPlot->replot();
}

void GraphDlg::Foilchanged(int iVal)
{ UpdateGraph(); }
void GraphDlg::checkBoxDoFitChanged(int state)
{ UpdateGraph(); }

void GraphDlg::Init(int iFolie)
{
	const TofConfig& conf = GlobalConfig::GetTofConfig();

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

	spinBoxFolie->setMinimum(1);
	spinBoxFolie->setMaximum(conf.GetFoilCount());
	spinBoxFolie->setValue(iFolie+1);

	//QwtLegend *m_plegend = new QwtLegend;
	//qwtPlot->insertLegend(m_plegend, QwtPlot::RightLegend);

	QObject::connect(btnPrint, SIGNAL(clicked()), this, SLOT(printPlot()));
	QObject::connect(checkBoxDoFit, SIGNAL(stateChanged(int)), this,
									SLOT(checkBoxDoFitChanged(int)));
	QObject::connect(spinBoxFolie, SIGNAL(valueChanged(int)), this,
								   SLOT(Foilchanged(int)));

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

	/*
	// Gesamtkurve
	m_curvetotal.setRenderHint(QwtPlotItem::RenderAntialiased);
	QPen pentotal = QPen(Qt::black);
	pentotal.setWidth(2);
	m_curvetotal.setPen(pentotal);
	m_curvetotal.attach(qwtPlot);
	*/
}

void GraphDlg::printPlot()
{
	QPrinter printer;
	printer.setOrientation(QPrinter::Landscape);
	QPrintDialog dialog(&printer);
	if(dialog.exec())
		qwtPlot->print(printer);
}

GraphDlg::GraphDlg(QWidget *pParent, TofImage* pTof) : QDialog(pParent),
													   m_pTofImg(pTof),
													   m_curve("Foil"),
													   m_curvefit("Fit"),
													   m_curvetotal("Total"),
													   m_plegend(0),
													   m_pgrid(0)
{
	setupUi(this);
	Init(0);
	UpdateGraph();
}

GraphDlg::GraphDlg(QWidget *pParent, TofImage* pTof, int iFolie)
														: QDialog(pParent),
														  m_pTofImg(pTof),
														  m_curve("Foil"),
														  m_curvefit("Fit"),
														  m_curvetotal("Total"),
														  m_plegend(0),
														  m_pgrid(0)
{
	setupUi(this);
	Init(iFolie);
	UpdateGraph();
}

GraphDlg::~GraphDlg()
{
	if(m_pgrid) delete m_pgrid;
	if(m_plegend) delete m_plegend;
}
// *****************************************************************************



// ********************* Contrasts vs Images ***********************************

ContrastsVsImagesDlg::ContrastsVsImagesDlg(CascadeWidget *pParent)
				 : QDialog(pParent), m_pwidget(pParent),
				   m_pgrid(0), m_ppanner(0)
{
	setupUi(this);

	listTofs->setSelectionMode(QAbstractItemView::ExtendedSelection);

	plot->setAutoReplot(false);
	plot->setCanvasBackground(QColor(255,255,255));
	plot->axisWidget(QwtPlot::xBottom)->setTitle("Image");
	plot->axisWidget(QwtPlot::yLeft)->setTitle("Contrast");


	m_pzoomer = new QwtPlotZoomer(plot->canvas());

	m_pzoomer->setSelectionFlags(QwtPicker::RectSelection |
								 QwtPicker::DragSelection);

	m_pzoomer->setMousePattern(QwtEventPattern::MouseSelect2,Qt::RightButton,
							   Qt::ControlModifier);
	m_pzoomer->setMousePattern(QwtEventPattern::MouseSelect3,Qt::RightButton);

	QColor c(Qt::darkBlue);
	m_pzoomer->setRubberBandPen(c);
	m_pzoomer->setTrackerPen(c);


	m_ppanner = new QwtPlotPanner(plot->canvas());
	m_ppanner->setMouseButton(Qt::MidButton);


	m_pgrid = new QwtPlotGrid;
	m_pgrid->enableXMin(true);
	m_pgrid->enableYMin(true);
	m_pgrid->setMajPen(QPen(Qt::black, 0, Qt::DotLine));
	m_pgrid->setMinPen(QPen(Qt::gray, 0 , Qt::DotLine));
	m_pgrid->attach(plot);

	QwtSymbol sym;
	sym.setStyle(QwtSymbol::Ellipse);
	sym.setPen(QColor(Qt::blue));
	sym.setBrush(QColor(Qt::blue));
	sym.setSize(5);

	m_curve.setRenderHint(QwtPlotItem::RenderAntialiased);
	QPen penfit = QPen(Qt::red);
	m_curve.setPen(penfit);
	m_curve.setSymbol(sym);
	m_curve.attach(plot);

	plot->setAxisScale(QwtPlot::yLeft, 0., 1.);

	connect(btnAdd, SIGNAL(clicked()), this, SLOT(AddFile()));
	connect(btnDelete, SIGNAL(clicked()), this, SLOT(DeleteFile()));
	connect(btnRoiLoad, SIGNAL(clicked()), this, SLOT(LoadRoi()));
	connect(btnRoiCurrent, SIGNAL(toggled(bool)),
			this, SLOT(SetRoiUseCurrent(bool)));
	connect(groupRoi, SIGNAL(toggled(bool)), this, SLOT(RoiGroupToggled()));
}

ContrastsVsImagesDlg::~ContrastsVsImagesDlg()
{
	if(m_pgrid) delete m_pgrid;
	if(m_pzoomer) delete m_pzoomer;
	if(m_ppanner) delete m_ppanner;
}

void ContrastsVsImagesDlg::UpdateGraph()
{
	// write a .dat file
	bool bDumpData = GlobalConfig::GetDumpFiles();

	bool bUseRoi = groupRoi->isChecked();
	bool bUseCurRoi = btnRoiCurrent->isChecked();
	QString strRoiFile = editRoi->text();

	TofImage tof;

	if(bUseRoi)
	{
		Roi &roi = tof.GetRoi();
		tof.UseRoi(true);

		if(bUseCurRoi)
		{
			Roi *pRoi = m_pwidget->GetCurRoi();
			if(pRoi==0)
			{
				logger.SetCurLogLevel(LOGLEVEL_ERR);
				logger << "Contrasts Dialog: No current ROI available.\n";

				tof.UseRoi(false);
			}
			else
			{
				// copy current roi
				roi = *pRoi;
			}
		}
		else // load roi from file
		{
			if(!roi.Load(strRoiFile.toAscii().data()))
			{
				logger.SetCurLogLevel(LOGLEVEL_ERR);
				logger << "Contrasts Dialog: Could not load ROI \""
					   << strRoiFile.toAscii().data() << "\".\n";

				tof.UseRoi(false);
			}
		}
	}

	const int iTofCnt = listTofs->count();

	double *pdx = new double[iTofCnt];
	double *pdy = new double[iTofCnt];
	double *pdy_err = new double[iTofCnt];

	int iFoilCount = tof.GetTofConfig().GetFoilCount();

	progressBar->setMaximum(iTofCnt*iFoilCount);
	progressBar->setValue(0);

	std::ofstream *ofstr = 0;
	if(bDumpData)
	{
		ofstr = new std::ofstream("contrasts.dat");
		(*ofstr) << std::scientific;
		(*ofstr) << "# contrast\tcontrast error\tphase\tphase error";

		for(int iFoil=0; iFoil<iFoilCount; ++iFoil)
		{
			(*ofstr) << "\tcontrast [" << iFoil << "]";
			(*ofstr) << "\tcontrast error [" << iFoil << "]";
			(*ofstr) << "\tphase [" << iFoil << "]";
			(*ofstr) << "\tphase error [" << iFoil << "]";
			(*ofstr) << "\tcounts [" << iFoil << "]";
		}

		(*ofstr) << "\n";
	}

	double dMax = 0., dMin=1.;

	double *pC = new double[iFoilCount];
	double *pC_err = new double[iFoilCount];
	double *pPh = new double[iFoilCount];
	double *pPh_err = new double[iFoilCount];

	for(int iItem=0; iItem<iTofCnt; ++iItem)
	{
		QListWidgetItem* pItem = listTofs->item(iItem);
		progressBar->setFormat(QString("%p% - ") + pItem->text());

		if(!tof.LoadFile(pItem->text().toAscii().data()))
		{
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "Contrasts Dialog: Could not load \""
				   << pItem->text().toAscii().data() << "\".\n";
			continue;
		}

		double dC=0., dC_err=0., dPh=0., dPh_err=0.;

		for(int iFoil=0; iFoil<iFoilCount; ++iFoil)
		{
			TmpGraph graph = tof.GetGraph(iFoil);
			bool bOk = graph.GetContrast(pC[iFoil], pPh[iFoil],
										pC_err[iFoil], pPh_err[iFoil]);

			dC += pC[iFoil];
			dC_err += pC_err[iFoil];
			dPh += pPh[iFoil];
			dPh_err += pPh_err[iFoil];

			progressBar->setValue(iItem*iFoilCount + iFoil + 1);
		}

		dC /= double(iFoilCount);
		dC_err /= double(iFoilCount);
		dPh /= double(iFoilCount);
		dPh_err /= double(iFoilCount);

		dMax = max(dMax, dC+dC_err);
		dMin = min(dMin, dC-dC_err);

		pdx[iItem] = iItem;
		pdy[iItem] = dC;
		pdy_err[iItem] = dC_err;

		if(bDumpData)
		{
			(*ofstr) << dC << "\t" << dC_err
					 << "\t" << dPh << "\t" << dPh_err;

			for(int iFoil=0; iFoil<iFoilCount; ++iFoil)
			{
				(*ofstr) << "\t" << pC[iFoil];
				(*ofstr) << "\t" << pC_err[iFoil];
				(*ofstr) << "\t" << pPh[iFoil];
				(*ofstr) << "\t" << pPh_err[iFoil];
				(*ofstr) << "\t" << tof.GetCounts(iFoil);
			}

			(*ofstr) << "\n";
		}
	}

	delete[] pC;
	delete[] pC_err;
	delete[] pPh;
	delete[] pPh_err;

	m_curve.setData(pdx, pdy, pdy_err, iTofCnt);

	delete[] pdx;
	delete[] pdy;

	//plot->setAxisScale(QwtPlot::yLeft, dMin, dMax);
	plot->setAxisScale(QwtPlot::xBottom, 0, iTofCnt);
	m_pzoomer->setZoomBase();

	plot->replot();

	if(bDumpData)
	{
		ofstr->flush();
		ofstr->close();
		delete ofstr;
	}
}

void ContrastsVsImagesDlg::RoiGroupToggled()
{
	UpdateGraph();
}

void ContrastsVsImagesDlg::LoadRoi()
{
	QString strFile = QFileDialog::getOpenFileName(this,
							"Open ROI File","",
							"ROI Files (*.roi *.roi);;XML Files (*.xml *.XML);;"
							"All Files (*)");

	editRoi->setText(strFile);
	UpdateGraph();
}

void ContrastsVsImagesDlg::SetRoiUseCurrent(bool bCur)
{
	editRoi->setEnabled(!bCur);
	btnRoiLoad->setEnabled(!bCur);

	UpdateGraph();
}

void ContrastsVsImagesDlg::AddFile()
{
	QStringList pads = QFileDialog::getOpenFileNames(this, "TOF files", "",
							"TOF Files (*.tof *.TOF);;All Files (*)");

	listTofs->addItems(pads);
	UpdateGraph();
}

void ContrastsVsImagesDlg::DeleteFile()
{
	QList<QListWidgetItem*> items = listTofs->selectedItems();

	// nothing specific selected -> clear all
	if(items.size() == 0)
		listTofs->clear();

	for(int i=0; i<items.size(); ++i)
	{
		if(items[i])
		{
			delete items[i];
			items[i] = 0;
		}
	}

	UpdateGraph();
}
