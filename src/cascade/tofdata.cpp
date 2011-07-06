// *****************************************************************************
// Module:
//   $Id$
//
// Author:
//   Tobias Weber <tweber@frm2.tum.de>
//
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


// *********************** PAD-Daten ***********************
PadData::PadData() : MainRasterData(QwtDoubleRect(0,
									Config_TofLoader::GetImageWidth(), 0,
									Config_TofLoader::GetImageHeight()))
{
}

PadData::PadData(const PadData& pad)
		: MainRasterData(QwtDoubleRect(0,
									Config_TofLoader::GetImageWidth(), 0,
									Config_TofLoader::GetImageHeight())),
		  PadImage(pad)
{
	m_bLog = pad.m_bLog;
}

PadData::~PadData()
{}

QwtRasterData *PadData::copy() const
{
	return new PadData(*this);
}

QwtDoubleInterval PadData::range() const
{
	if(m_puiDaten==NULL) return QwtDoubleInterval(0.,1.);

	if(m_bLog)
	{
		double dTmpMax = m_iMax,
		       dTmpMin = m_iMin;

		if(dTmpMax>0.)
			dTmpMax = log10(dTmpMax);
		else
			dTmpMax=Config_TofLoader::GetLogLowerRange();

		if(dTmpMin>0.)
			dTmpMin = log10(dTmpMin);
		else
			dTmpMin=Config_TofLoader::GetLogLowerRange();

		if(dTmpMax!=dTmpMax)
			dTmpMax=0.;
		if(dTmpMin!=dTmpMin)
			dTmpMin=0.;

		return QwtDoubleInterval(dTmpMin,dTmpMax);
	}
	else
	{
		return QwtDoubleInterval(m_iMin,m_iMax);
	}
}


double PadData::value(double x, double y) const
{
	double dRet=(double)GetData((int)x,(int)y);

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

double PadData::GetValueRaw(int x, int y) const
{
	return (double)GetData(x,y);
}

// ***********************************************************


// *********************** TOF-Daten ***********************
Data2D::Data2D(const QwtDoubleRect& rect)
		: MainRasterData(rect), m_bPhaseData(0)
{}

Data2D::Data2D() : MainRasterData(QwtDoubleRect(0,
								  Config_TofLoader::GetImageWidth(), 0,
								  Config_TofLoader::GetImageHeight()))
{}

Data2D::Data2D(const Data2D& data2d)
		: MainRasterData(QwtDoubleRect(0,data2d.m_iW,0,data2d.m_iH)),
		  TmpImage(data2d)
{
	this->m_bLog = data2d.m_bLog;
	this->m_bPhaseData = data2d.m_bPhaseData;
}

Data2D::~Data2D()
{
	clearData();
}

// wegen Achsen-Range
void Data2D::SetPhaseData(bool bPhaseData)
{
	m_bPhaseData = bPhaseData;
}

void Data2D::clearData()
{
	if(m_puiDaten!=NULL)
	{
		delete[] m_puiDaten;
		m_puiDaten = NULL;
	}
	if(m_pdDaten!=NULL)
	{
		delete[] m_pdDaten;
		m_pdDaten = NULL;
	}
}

QwtRasterData *Data2D::copy() const
{
	return new Data2D(*this);
}

QwtDoubleInterval Data2D::range() const
{
	if(m_puiDaten==NULL && m_pdDaten==NULL)
		return QwtDoubleInterval(0.,1.);

	double dTmpMax, dTmpMin;
	if(m_bPhaseData)
	{
		dTmpMax=360.;
		dTmpMin=0.;
	}
	else
	{
		dTmpMax = m_dMax;
		dTmpMin = m_dMin;
	}

	if(m_bLog)
	{
		if(dTmpMax>0.)
			dTmpMax=log10(dTmpMax);
		else
			dTmpMax=Config_TofLoader::GetLogLowerRange();
		if(dTmpMin>0.)
			dTmpMin=log10(dTmpMin);
		else
			dTmpMin=Config_TofLoader::GetLogLowerRange();

		if(dTmpMax!=dTmpMax) dTmpMax=0.;
		if(dTmpMin!=dTmpMin) dTmpMin=0.;

		return QwtDoubleInterval(dTmpMin,dTmpMax);
	}
	else
		return QwtDoubleInterval(dTmpMin,dTmpMax);
}

double Data2D::value(double x, double y) const
{
	double dRet=(double)GetData((int)x,(int)y);

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
	return (double)GetData(x,y);
}

// **********************************************************
