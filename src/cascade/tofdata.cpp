// *****************************************************************************
// NICOS-NG, the Networked Instrument Control System of the FRM-II
// Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
// Klassen, um die TOF- und PAD-Datentypen mit Qwt zu nutzen

#include <limits>
#include <math.h>
#include <iostream>
#include "tofdata.h"

MainRasterData::MainRasterData(const QwtDoubleRect& rect)
				: QwtRasterData(rect), m_bLog(1)
{
}

void MainRasterData::SetLog10(bool bLog10)
{
	m_bLog = bLog10;
}

bool MainRasterData::GetLog10(void) const
{
	return m_bLog;
}


// *********************************************************
Data2D::Data2D(const QwtDoubleRect& rect)
		: MainRasterData(rect), m_bPhaseData(0), m_pImg(0)
{}

Data2D::Data2D()
	: MainRasterData(QwtDoubleRect(0,
					 GlobalConfig::GetTofConfig().GetImageWidth(), 0,
					 GlobalConfig::GetTofConfig().GetImageHeight())),
					 m_bPhaseData(0), m_pImg(0)
{}

Data2D::Data2D(const Data2D& data2d)
		:  MainRasterData(QwtDoubleRect(0, data2d.GetWidth(),
										0, data2d.GetHeight()))
{
	this->m_bLog = data2d.m_bLog;
	this->m_bPhaseData = data2d.m_bPhaseData;
	this->m_pImg = data2d.m_pImg;
}

Data2D::~Data2D()
{
	clearData();
}

void Data2D::SetImage(BasicImage* pImg) { m_pImg = pImg; }
BasicImage* Data2D::GetImage() { return m_pImg; }

int Data2D::GetWidth() const
{
	if(!m_pImg) return 0;
	return m_pImg->GetWidth();
}

int Data2D::GetHeight() const
{
	if(!m_pImg) return 0;
	return m_pImg->GetHeight();
}

// wegen Achsen-Range
void Data2D::SetPhaseData(bool bPhaseData)
{
	m_bPhaseData = bPhaseData;
}

void Data2D::clearData()
{
	m_pImg = 0;
}

QwtRasterData *Data2D::copy() const
{
	return new Data2D(*this);
}

QwtDoubleInterval Data2D::range() const
{
	if(m_pImg == 0)
		return QwtDoubleInterval(0.,1.);

	double dTmpMax, dTmpMin;
	if(m_bPhaseData)
	{
		dTmpMax=360.;
		dTmpMin=0.;
	}
	else
	{
		dTmpMax = m_pImg->GetDoubleMax();
		dTmpMin = m_pImg->GetDoubleMin();
	}

	if(m_bLog)
	{
		if(dTmpMax>0.)
			dTmpMax=log10(dTmpMax);
		else
			dTmpMax=GlobalConfig::GetLogLowerRange();
		if(dTmpMin>0.)
			dTmpMin=log10(dTmpMin);
		else
			dTmpMin=GlobalConfig::GetLogLowerRange();

		if(dTmpMax!=dTmpMax)
			dTmpMax=0.;
		if(dTmpMin!=dTmpMin)
			dTmpMin=0.;

		return QwtDoubleInterval(dTmpMin,dTmpMax);
	}
	else
		return QwtDoubleInterval(dTmpMin,dTmpMax);
}

double Data2D::value(double x, double y) const
{
	if(m_pImg == 0) return 0.;

	double dRet = m_pImg->GetDoubleData((int)x,(int)y);

	if(m_bLog)
	{
		if(dRet>0.)
			dRet = log10(dRet);
		else
			// ungültige Werte weit außerhalb der Range verlagern
			dRet = -std::numeric_limits<double>::max();
	}

	if(dRet!=dRet) dRet=0.;
	return dRet;
}

double Data2D::GetValueRaw(int x, int y) const
{
	if(m_pImg == 0) return 0.;

	return m_pImg->GetDoubleData(x,y);
}

// **********************************************************
