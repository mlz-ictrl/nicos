// *****************************************************************************
// NICOS, the Networked Instrument Control System of the FRM-II
// Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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
//
// Plotter initially based on "spectrogram" qwt sample code
//

#include "plotter.h"
#include "../auxiliary/helper.h"

#include <sstream>
#include <qprinter.h>
#include <qprintdialog.h>
#include <qwt_scale_widget.h>
#include <qwt_plot_layout.h>

//------------------------------------------------------------------------------
// picker

MainPicker::MainPicker(QwtPlotCanvas* pcanvas)
		   : QwtPlotPicker(pcanvas),
			 m_iRoiDrawMode(ROI_DRAW_RECT), m_pCurRoi(0)
{
	setSelectionFlags(QwtPicker::RectSelection | QwtPicker::DragSelection);

	QColor c(Qt::darkBlue);
	setRubberBandPen(c);
	setTrackerPen(c);

	setRubberBand(RectRubberBand);
	//setTrackerMode(QwtPicker::ActiveOnly);
	setTrackerMode(AlwaysOn);

	connect((QwtPlotPicker*)this, SIGNAL(selected(const QwtDoubleRect&)),
			this, SLOT(selectedRect (const QwtDoubleRect&)));

	connect((QwtPlotPicker*)this, SIGNAL(selected(const QwtArray<QwtDoublePoint> &)),
			this, SLOT(selectedPoly(const QwtArray<QwtDoublePoint> &)));
}

MainPicker::~MainPicker()
{}

QwtText MainPicker::trackerText(const QwtDoublePoint &pos) const
{
	const double dX = pos.x();
	const double dY = pos.y();

	QString str;
	str += "Pixel: ";
	str += QString::number(int(dX));
	str += ", ";
	str += QString::number(int(dY));
	str += "\n";

	if(isActive())
	{
		switch(m_iRoiDrawMode)
		{
			case ROI_DRAW_RECT:
				str += "Drawing Rectangle";
				break;
			case ROI_DRAW_CIRC:
				str += "Drawing Circle";
				break;
			case ROI_DRAW_CIRCRING:
				str += "Drawing Circle Ring";
				break;
			case ROI_DRAW_CIRCSEG:
				str += "Drawing Circle Segment";
				break;
			case ROI_DRAW_ELLIPSE:
				str += "Drawing Ellipse";
				break;
			case ROI_DRAW_POLYGON:
				str += "Drawing Polygon";
				break;
		}
	}
	else
	{
		if(m_pCurRoi)
		{
			if(m_pCurRoi->IsInside(dX, dY))
				str += "cursor inside roi";
			else
				str += "cursor outside roi";

			double dFraction = m_pCurRoi->HowMuchInside(dX, dY);
			str += "\npixel ";
			str += QString::number(dFraction*100.);
			str += "% inside roi";
		}
	}

	QwtText text = str;
	QColor bg(Qt::white);
	bg.setAlpha(200);
	text.setBackgroundBrush(QBrush(bg));
	return text;
}

void MainPicker::SetRoiDrawMode(int iMode)
{
	m_iRoiDrawMode = iMode;

	switch(iMode)
	{
		case ROI_DRAW_RECT:
			setSelectionFlags(QwtPicker::RectSelection);
			setRubberBand(RectRubberBand);
			break;
		case ROI_DRAW_CIRC:
			setSelectionFlags(QwtPicker::RectSelection);
			setRubberBand(EllipseRubberBand);	// !!
			break;
		case ROI_DRAW_CIRCRING:
			setSelectionFlags(QwtPicker::RectSelection);
			setRubberBand(EllipseRubberBand);	// !!
			break;
		case ROI_DRAW_CIRCSEG:
			setSelectionFlags(QwtPicker::RectSelection);
			setRubberBand(EllipseRubberBand);	// !!
			break;
		case ROI_DRAW_ELLIPSE:
			setSelectionFlags(QwtPicker::RectSelection);
			setRubberBand(EllipseRubberBand);
			break;
		case ROI_DRAW_POLYGON:
			setSelectionFlags(QwtPicker::PolygonSelection);
			setRubberBand(PolygonRubberBand);
			break;
	}
}

void MainPicker::selectedPoly(const QwtArray<QwtDoublePoint>& poly)
{
	if(m_pCurRoi == NULL)
		return;

	// minimum of 3 vertices needed
	if(poly.size()<=2)
		return;

	RoiPolygon *pElem = new RoiPolygon();
	for(int i=0; i<poly.size(); ++i)
	{
		const QwtDoublePoint& pt = poly[i];

		Vec2d<double> vertex(pt.x(), pt.y());
		pElem->AddVertex(vertex);
	}

	m_pCurRoi->add(pElem);
	emit RoiHasChanged();
}

void MainPicker::selectedRect(const QwtDoubleRect &rect)
{
	if(m_pCurRoi == NULL)
		return;

	Vec2d<int> bottomleft;
	Vec2d<int> topright;

	bottomleft[0] = rect.bottomLeft().x();
	bottomleft[1] = rect.bottomLeft().y();
	topright[0] = rect.topRight().x();
	topright[1] = rect.topRight().y();

	RoiElement* pElem = 0;

	switch(m_iRoiDrawMode)
	{
		case ROI_DRAW_RECT:
		{
			pElem = new RoiRect(bottomleft.cast<double>(),
								topright.cast<double>());
			break;
		}

		case ROI_DRAW_CIRC:
		{
			double dRadius = double(topright[0] - bottomleft[0]) * 0.5;
			Vec2d<double> vecCenter = (topright.cast<double>()-
									  bottomleft.cast<double>()) * 0.5 +
									  bottomleft.cast<double>();

			pElem = new RoiCircle(vecCenter, dRadius);
			break;
		}

		case ROI_DRAW_CIRCRING:
		{
			double dRadius = double(topright[0] - bottomleft[0]) * 0.5;
			Vec2d<double> vecCenter = (topright.cast<double>()-
									  bottomleft.cast<double>()) * 0.5 +
									  bottomleft.cast<double>();

			pElem = new RoiCircleRing(vecCenter, dRadius-4., dRadius+4.);
			break;
		}

		case ROI_DRAW_CIRCSEG:
		{
			double dRadius = double(topright[0] - bottomleft[0]) * 0.5;
			Vec2d<double> vecCenter = (topright.cast<double>()-
									  bottomleft.cast<double>()) * 0.5 +
									  bottomleft.cast<double>();

			pElem = new RoiCircleSegment(vecCenter, dRadius-4., dRadius+4.,
										0., 90.);
			break;
		}

		case ROI_DRAW_ELLIPSE:
		{
			double dRadiusX = double(topright[0] - bottomleft[0]) * 0.5;
			double dRadiusY = double(topright[1] - bottomleft[1]) * 0.5;
			Vec2d<double> vecCenter = (topright.cast<double>()-
									  bottomleft.cast<double>()) * 0.5 +
									  bottomleft.cast<double>();

			pElem = new RoiEllipse(vecCenter, dRadiusX, dRadiusY);
			break;
		}
	}

	if(pElem)
	{
		m_pCurRoi->add(pElem);
		emit RoiHasChanged();
	}
}

int MainPicker::GetRoiDrawMode() const { return m_iRoiDrawMode; }
void MainPicker::SetCurRoi(Roi* pRoi) { m_pCurRoi = pRoi; }



//------------------------------------------------------------------------------
// zoomer

MainZoomer::MainZoomer(QwtPlotCanvas *canvas, const QwtPlotSpectrogram* pData)
										: QwtPlotZoomer(canvas), m_pData(pData)
{
	setSelectionFlags(QwtPicker::RectSelection | QwtPicker::DragSelection);

	setMousePattern(QwtEventPattern::MouseSelect2,Qt::RightButton,
													Qt::ControlModifier);
	setMousePattern(QwtEventPattern::MouseSelect3,Qt::RightButton);

	QColor c(Qt::darkBlue);
	setRubberBandPen(c);
	setTrackerPen(c);

	setTrackerMode(AlwaysOn);
}

MainZoomer::~MainZoomer()
{}

QwtText MainZoomer::trackerText(const QwtDoublePoint &pos) const
{
	QString str = "Pixel: ";
	str += QString::number(int(pos.x()));
	str += ", ";
	str += QString::number(int(pos.y()));

	const MainRasterData& rasterdata = (const MainRasterData&)m_pData->data();

	str += "\nValue: ";

	std::ostringstream ostr;
	SetNumberGrouping(ostr);
	ostr << rasterdata.GetValueRaw(pos.x(),pos.y());
	str += ostr.str().c_str();

	QwtText text = str;
	QColor bg(Qt::white);
	bg.setAlpha(200);
	text.setBackgroundBrush(QBrush(bg));
	return text;
}



//------------------------------------------------------------------------------
// panner

MainPanner::MainPanner(QwtPlotCanvas *canvas) : QwtPlotPanner(canvas)
{
	setAxisEnabled(QwtPlot::yRight, false);
	setMouseButton(Qt::MidButton);
}

MainPanner::~MainPanner()
{}




//------------------------------------------------------------------------------
// plot

Plot::Plot(QWidget *parent) : QwtPlot(parent), m_pSpectrogram(0),
							  m_pZoomer(0), m_pPanner(0), m_pRoiPicker(0),
							  m_pImage(0)
{
	InitPlot();
}

Plot::~Plot()
{
	DeinitPlot();
}

void Plot::InitPlot()
{
	DeinitPlot();

	axisWidget(QwtPlot::xBottom)->setTitle("x Pixels");
	axisWidget(QwtPlot::yLeft)->setTitle("y Pixels");

	m_pSpectrogram = new QwtPlotSpectrogram();
	m_pSpectrogram->setData(MainRasterData());		// Dummy-Objekt
	m_pSpectrogram->setDisplayMode(QwtPlotSpectrogram::ImageMode, true);
	m_pSpectrogram->setDisplayMode(QwtPlotSpectrogram::ContourMode, false);
	m_pSpectrogram->attach(this);

	setCanvasBackground(QColor(255,255,255));
	SetColorMap(false);

	enableAxis(QwtPlot::yRight);
	axisWidget(QwtPlot::yRight)->setColorBarEnabled(true);

	ChangeRange();
	ChangeRange_xy();

	plotLayout()->setAlignCanvasToScales(true);

	m_pZoomer = new MainZoomer(canvas(), m_pSpectrogram);
	m_pPanner = new MainPanner(canvas());

	m_pRoiPicker = new MainPicker(canvas());
	m_pRoiPicker->setEnabled(false);

	// avoid jumping of the layout
	axisScaleDraw(QwtPlot::yLeft)->setMinimumExtent(35);
	axisScaleDraw(QwtPlot::yRight)->setMinimumExtent(60);
	axisWidget(QwtPlot::yRight)->setMinBorderDist(25,0);
}

/*
void Plot::ChangeLog(bool bLog10)
{
	if(bLog10)
		axisScaleDraw(QwtPlot::yRight)->setMinimumExtent(50);
	else
		axisScaleDraw(QwtPlot::yRight)->setMinimumExtent(75);
}
*/

void Plot::DeinitPlot()
{
	m_pImage = 0;
	if(m_pZoomer) { delete m_pZoomer; m_pZoomer=0; }
	if(m_pPanner) { delete m_pPanner; m_pPanner=0; }
	if(m_pRoiPicker) { delete m_pRoiPicker; m_pRoiPicker=0; }
	if(m_pSpectrogram) { delete m_pSpectrogram; m_pSpectrogram=0; }
}

void Plot::ChangeRange()
{
	const QwtDoubleInterval& range = m_pSpectrogram->data().range();

	setAxisScale(QwtPlot::yRight, range.minValue(), range.maxValue());
	axisWidget(QwtPlot::yRight)->setColorMap(range, m_pSpectrogram->colorMap());
}

void Plot::ChangeRange_xy()
{
	if(m_pImage)
	{
		// use dimensions of image

		setAxisScale(QwtPlot::yLeft, 0, m_pImage->GetHeight());
		setAxisScale(QwtPlot::xBottom, 0, m_pImage->GetWidth());
	}
	else
	{
		// otherwise: global config

		const PadConfig& conf = GlobalConfig::GetTofConfig();
		setAxisScale(QwtPlot::yLeft, 0, conf.GetImageHeight());
		setAxisScale(QwtPlot::xBottom, 0, conf.GetImageWidth());
	}

	if(m_pZoomer)
		m_pZoomer->setZoomBase();
}

QwtPlotZoomer* Plot::GetZoomer() { return m_pZoomer; }
QwtPlotPanner* Plot::GetPanner() { return m_pPanner; }
QwtPlotPicker* Plot::GetRoiPicker() { return m_pRoiPicker; }

const QwtRasterData* Plot::GetData() const
{
	return &m_pSpectrogram->data();
}

void Plot::SetData(MainRasterData* pData, bool bUpdate)
{
	m_pImage = pData->GetImage();

	if(bUpdate)
	{
		m_pSpectrogram->setData(*pData);
		ChangeRange();
	}
}

void Plot::SetColorMap(bool bCyclic)
{
	if(m_pSpectrogram==NULL) return;

	if(bCyclic)	// F��r Phasen
	{
		QwtLinearColorMap colorMap(Qt::blue, Qt::blue);
		colorMap.addColorStop(0.0, Qt::blue);
		colorMap.addColorStop(0.75, Qt::red);
		colorMap.addColorStop(0.5, Qt::yellow);
		colorMap.addColorStop(0.25, Qt::cyan);
		colorMap.addColorStop(1.0, Qt::blue);
		m_pSpectrogram->setColorMap(colorMap);
	}
	else
	{
		QwtLinearColorMap colorMap(Qt::blue, Qt::red);
		colorMap.addColorStop(0.0, Qt::blue);
		colorMap.addColorStop(0.33, Qt::cyan);
		colorMap.addColorStop(0.66, Qt::yellow);
		colorMap.addColorStop(1.0, Qt::red);
		m_pSpectrogram->setColorMap(colorMap);
	}
}

void Plot::printPlot()
{
	QPrinter printer;
	printer.setColorMode(QPrinter::Color);
	printer.setOrientation(QPrinter::Landscape);

	QPrintDialog dialog(&printer);
	if(dialog.exec())
		print(printer);
}

void Plot::replot()
{
	QwtPlot::replot();
}

/*
#ifdef __MOC_EXTERN_BUILD__
//	// Qt-Metaobjekte
	#include "plotter.moc"
#endif
*/
