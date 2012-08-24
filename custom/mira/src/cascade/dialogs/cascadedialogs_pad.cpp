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

// *********************** Integration Dialog **********************************

IntegrationDlg::IntegrationDlg(CascadeWidget *pParent)
				: QDialog(pParent), m_pwidget(pParent),
				  m_pzoomer(0), m_ppanner(0),
				  m_bAutoUpdate(true)
{
	setupUi(this);

	plot->setAutoReplot(false);
	plot->setCanvasBackground(QColor(255,255,255));
	plot->axisWidget(QwtPlot::xBottom)->setTitle("Radius");
	plot->axisWidget(QwtPlot::yLeft)->setTitle("Counts");

	m_pgrid = new QwtPlotGrid;
	m_pgrid->enableXMin(true);
	m_pgrid->enableYMin(true);
	m_pgrid->setMajPen(QPen(Qt::black, 0, Qt::DotLine));
	m_pgrid->setMinPen(QPen(Qt::gray, 0 , Qt::DotLine));
	m_pgrid->attach(plot);


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

	connect(btnBeamCenter, SIGNAL(clicked()), this, SLOT(UseBeamCenter()));
	connect(btnImageCenter, SIGNAL(clicked()), this, SLOT(UseImageCenter()));
	connect(btnLog10, SIGNAL(toggled(bool)), this, SLOT(SetLog10(bool)));

	connect(doubleSpinBoxX, SIGNAL(valueChanged(double)),
			this, SLOT(UpdateGraph()));
	connect(doubleSpinBoxY, SIGNAL(valueChanged(double)),
			this, SLOT(UpdateGraph()));

	connect(chkAngMean, SIGNAL(stateChanged(int)), this, SLOT(UpdateGraph()));
}

IntegrationDlg::~IntegrationDlg()
{
	if(m_pgrid) delete m_pgrid;
	if(m_pzoomer) delete m_pzoomer;
	if(m_ppanner) delete m_ppanner;
}

void IntegrationDlg::UpdateGraph()
{
	if(!m_bAutoUpdate)
		return;

	bool bLog10 = btnLog10->isChecked();
	bool bAngMean = (chkAngMean->checkState()==Qt::Checked);

	TmpImage tmpImg = GetRoiImage();

	const double dRadInc = 1.;
	const double dAngInc = 0.01;

	// TODO: Use beam center!
	Vec2d<double> vecCenter;
	vecCenter[0] = doubleSpinBoxX->value();
	vecCenter[1] = doubleSpinBoxY->value();

	TmpGraph tmpGraph = tmpImg.
					GetRadialIntegration(dAngInc, dRadInc, vecCenter, bAngMean);

	double *pdx = new double[tmpGraph.GetWidth()];
	double *pdy = new double[tmpGraph.GetWidth()];

	double dMax = 1.;
	for(int i=0; i<tmpGraph.GetWidth(); ++i)
		dMax = max(dMax, double(tmpGraph.GetData(i)));

	for(int i=0; i<tmpGraph.GetWidth(); ++i)
	{
		pdx[i] = double(i) * dRadInc;
		pdy[i] = double(tmpGraph.GetData(i)) /* / dMax*/;

		if(bLog10)
			pdy[i] = safe_log10(pdy[i]);
	}
	m_curve.setData(pdx,pdy,tmpGraph.GetWidth());
	delete[] pdx;
	delete[] pdy;

	if(bLog10)
		dMax = safe_log10(dMax);

	plot->setAxisScale(QwtPlot::yLeft, GlobalConfig::GetLogLowerRange(), dMax);
	plot->setAxisScale(QwtPlot::xBottom, 0, (tmpGraph.GetWidth()-1)*dRadInc);
	m_pzoomer->setZoomBase();

	plot->replot();
}

void IntegrationDlg::UseBeamCenter()
{
	TmpImage tmpImg;

	if(m_pwidget->IsTofLoaded())
		tmpImg = m_pwidget->GetTof()->GetOverview();
	else
		tmpImg.ConvertPAD(m_pwidget->GetPad());

	double dAmp=0., dCenterX=0., dCenterY=0., dSpreadX=0., dSpreadY=0.;
	bool bOk = tmpImg.FitGaussian(dAmp,dCenterX,dCenterY,dSpreadX,dSpreadY);

	if(bOk)
	{
		std::ostringstream ostr;
		ostr << "Gaussian fit with amp=" << dAmp
			 << ", x=" << dCenterX << ", y="<<dCenterY
			 << ", sx=" << dSpreadX << ", sy=" << dSpreadY;

		logger.SetCurLogLevel(LOGLEVEL_INFO);
		logger << "Integration Dialog: " << ostr.str() << "\n";
	}
	else
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Integration Dialog: No valid Gaussian fit found.\n";
	}

	m_bAutoUpdate = false;
	doubleSpinBoxX->setValue(dCenterX);
	doubleSpinBoxY->setValue(dCenterY);
	m_bAutoUpdate = true;

	UpdateGraph();
}

void IntegrationDlg::UseImageCenter()
{
	TmpImage tmpImg = GetRoiImage();

	double dX = double(tmpImg.GetWidth()) * .5;
	double dY = double(tmpImg.GetHeight()) * .5;

	m_bAutoUpdate = false;
	doubleSpinBoxX->setValue(dX);
	doubleSpinBoxY->setValue(dY);
	m_bAutoUpdate = true;

	UpdateGraph();
}

TmpImage IntegrationDlg::GetRoiImage()
{
	TmpImage tmpImg;

	if(m_pwidget->IsPadLoaded())
		tmpImg = m_pwidget->GetPad()->GetRoiImage();
	else if(m_pwidget->IsTofLoaded())
		tmpImg = m_pwidget->GetTof()->GetOverview(true);

	return tmpImg;
}

void IntegrationDlg::SetLog10(bool bLog10)
{
	plot->axisWidget(QwtPlot::yLeft)->setTitle(bLog10?"Counts 10^":"Counts");
	UpdateGraph();
}

// *****************************************************************************



// ********************* Counts vs Images **************************************

CountsVsImagesDlg::CountsVsImagesDlg(CascadeWidget *pParent)
				 : QDialog(pParent), m_pwidget(pParent),
				   m_pgrid(0), m_ppanner(0)
{
	setupUi(this);

	listPads->setSelectionMode(QAbstractItemView::ExtendedSelection);

	plot->setAutoReplot(false);
	plot->setCanvasBackground(QColor(255,255,255));
	plot->axisWidget(QwtPlot::xBottom)->setTitle("Image");
	plot->axisWidget(QwtPlot::yLeft)->setTitle("Counts");


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

	connect(btnAdd, SIGNAL(clicked()), this, SLOT(AddFile()));
	connect(btnDelete, SIGNAL(clicked()), this, SLOT(DeleteFile()));
	connect(btnRoiLoad, SIGNAL(clicked()), this, SLOT(LoadRoi()));
	connect(btnRoiCurrent, SIGNAL(toggled(bool)),
			this, SLOT(SetRoiUseCurrent(bool)));
	connect(groupRoi, SIGNAL(toggled(bool)), this, SLOT(RoiGroupToggled()));
	connect(checkCorrect, SIGNAL(toggled(bool)), this, SLOT(UpdateGraph()));
}

CountsVsImagesDlg::~CountsVsImagesDlg()
{
	if(m_pgrid) delete m_pgrid;
	if(m_pzoomer) delete m_pzoomer;
	if(m_ppanner) delete m_ppanner;
}

void CountsVsImagesDlg::UpdateGraph()
{
	const int iPadCnt = listPads->count();
	if(iPadCnt == 0)
		return;

	bool bUseRoi = groupRoi->isChecked();
	bool bUseCurRoi = btnRoiCurrent->isChecked();
	QString strRoiFile = editRoi->text();

	PadImage pad;
	TofImage tof;

	// write a .dat file
	bool bDumpData = GlobalConfig::GetDumpFiles();
	std::ofstream *ofstr = 0;
	if(bDumpData)
	{
		ofstr = new std::ofstream("counts.dat");
		(*ofstr) << std::scientific;
		(*ofstr) << "# file\tcounts\n";
	}

	if(bUseRoi)
	{
		Roi &roi = pad.GetRoi();
		Roi &roi_tof = tof.GetRoi();
		pad.UseRoi(true);
		tof.UseRoi(true);

		if(bUseCurRoi)
		{
			Roi *pRoi = m_pwidget->GetCurRoi();
			if(pRoi==0)
			{
				logger.SetCurLogLevel(LOGLEVEL_ERR);
				logger << "Counts Dialog: No current ROI available.\n";

				pad.UseRoi(false);
				tof.UseRoi(false);
			}
			else
			{
				// copy current roi
				roi = *pRoi;
				roi_tof = *pRoi;
			}
		}
		else // load roi from file
		{
			if(!roi.Load(strRoiFile.toAscii().data()))
			{
				logger.SetCurLogLevel(LOGLEVEL_ERR);
				logger << "Counts Dialog: Could not load ROI \""
					   << strRoiFile.toAscii().data() << "\".\n";

				pad.UseRoi(false);
				tof.UseRoi(false);
			}
			else
			{
				roi_tof = roi;
			}
		}
	}

	double *pdx = new double[iPadCnt];
	double *pdy = new double[iPadCnt];

	progressBar->setMaximum(iPadCnt);
	progressBar->setValue(0);

	unsigned int uiMax = 0;
	for(int iItem=0; iItem<iPadCnt; ++iItem)
	{
		pdx[iItem] = iItem;
		pdy[iItem] = 0;

		QListWidgetItem* pItem = listPads->item(iItem);
		const char* pcFile = pItem->text().toAscii().data();

		progressBar->setFormat(QString("%p% - ") + pItem->text());

		Countable* pcnt = 0;
		int iLoadStatus = 0;
		if(strcasecmp(GetFileEnding(pcFile).c_str(), "tof")==0)
		{
			iLoadStatus = tof.LoadFile(pcFile);
			pcnt = &tof;
		}
		else if(strcasecmp(GetFileEnding(pcFile).c_str(), "pad")==0)
		{
			iLoadStatus = pad.LoadFile(pcFile);
			pcnt = &pad;
		}
		else
		{
			logger.SetCurLogLevel(LOGLEVEL_WARN);
			logger << "Counts Dialog: Invalid file extension in \""
				   << pcFile << "\". Ignoring. \n";
			continue;
		}

		if(!iLoadStatus)
		{
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "Counts Dialog: Could not load \""
				   << pItem->text().toAscii().data() << "\".\n";
			continue;
		}


		unsigned int uiCnts = 0;

		if(checkCorrect->isChecked())
			uiCnts = pcnt->GetCountsSubtractBackground();
		else
			uiCnts = pcnt->GetCounts();

		uiMax = max(uiMax, uiCnts);

		//pdx[iItem] = iItem;
		pdy[iItem] = uiCnts;

		progressBar->setValue(iItem + 1);

		if(bDumpData)
		{
			(*ofstr) << iItem << "\t" << uiCnts;
			(*ofstr) << "\n";
		}
	}

	m_curve.setData(pdx, pdy, iPadCnt);

	delete[] pdx;
	delete[] pdy;

	plot->setAxisScale(QwtPlot::yLeft, 0, uiMax);
	plot->setAxisScale(QwtPlot::xBottom, 0, iPadCnt);
	m_pzoomer->setZoomBase();

	plot->replot();

	if(bDumpData)
	{
		ofstr->flush();
		ofstr->close();
		delete ofstr;
	}
}

void CountsVsImagesDlg::RoiGroupToggled()
{
	bool bUseRoi = groupRoi->isChecked();
	bool bUseCurRoi = btnRoiCurrent->isChecked();
	QString strRoiFile = editRoi->text();

	if((bUseRoi && (bUseCurRoi || editRoi->text()!="")) || !bUseRoi)
		UpdateGraph();
}

void CountsVsImagesDlg::LoadRoi()
{
	QString strFile = QFileDialog::getOpenFileName(this,
							"Open ROI File","",
							"ROI Files (*.roi *.roi);;XML Files (*.xml *.XML);;"
							"All Files (*)");

	editRoi->setText(strFile);
	UpdateGraph();
}

void CountsVsImagesDlg::SetRoiUseCurrent(bool bCur)
{
	editRoi->setEnabled(!bCur);
	btnRoiLoad->setEnabled(!bCur);

	UpdateGraph();
}

void CountsVsImagesDlg::AddFile()
{
	QString strDir(GlobalConfig::GetCurDir().c_str());

	QStringList pads = QFileDialog::getOpenFileNames(
					this, "PAD/TOF files", strDir,
					"PAD/TOF Files (*.pad *.PAD *.tof *.TOF);;All Files (*)");

	listPads->addItems(pads);
	UpdateGraph();
}

void CountsVsImagesDlg::DeleteFile()
{
	QList<QListWidgetItem*> items = listPads->selectedItems();

	// nothing specific selected -> clear all
	if(items.size() == 0)
		listPads->clear();

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
