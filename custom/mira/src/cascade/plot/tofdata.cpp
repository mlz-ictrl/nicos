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
// Klassen, um die TOF- und PAD-Datentypen mit Qwt zu nutzen

#include <limits>
#include <math.h>
#include <iostream>

#include "tofdata.h"
#include "../auxiliary/helper.h"

MainRasterData::MainRasterData(const QwtDoubleRect& rect)
				: QwtRasterData(rect), m_bLog(1),
				  m_bPhaseData(0), m_pImg(0), m_bAutoRange(1)
{}

void MainRasterData::SetLog10(bool bLog10) { m_bLog = bLog10; }
bool MainRasterData::GetLog10(void) const { return m_bLog; }

MainRasterData::MainRasterData()
	: QwtRasterData(QwtDoubleRect(0,
					 GlobalConfig::GetTofConfig().GetImageWidth(), 0,
					 GlobalConfig::GetTofConfig().GetImageHeight())),
					 m_bLog(1), m_bPhaseData(0), m_pImg(0), m_bAutoRange(1)
{}

MainRasterData::MainRasterData(const MainRasterData& data2d)
		:  QwtRasterData(QwtDoubleRect(0, data2d.GetWidth(),
									   0, data2d.GetHeight()))
{
	this->m_bLog = data2d.m_bLog;
	this->m_bPhaseData = data2d.m_bPhaseData;
	this->m_pImg = data2d.m_pImg;
	this->m_bAutoRange = data2d.m_bAutoRange;
	this->m_dRange[0] = data2d.m_dRange[0];
	this->m_dRange[1] = data2d.m_dRange[1];
}

MainRasterData::~MainRasterData() { clearData(); }

void MainRasterData::SetImage(BasicImage** pImg) { m_pImg = pImg; }
BasicImage* MainRasterData::GetImage()
{
	if(m_pImg)
		return *m_pImg;
	return 0;
}

int MainRasterData::GetWidth() const
{
	if(!m_pImg || !*m_pImg)
		return GlobalConfig::GetTofConfig().GetImageWidth();
	return (*m_pImg)->GetWidth();
}

int MainRasterData::GetHeight() const
{
	if(!m_pImg || !*m_pImg)
		return GlobalConfig::GetTofConfig().GetImageHeight();
	return (*m_pImg)->GetHeight();
}

// wegen Achsen-Range
void MainRasterData::SetPhaseData(bool bPhaseData)
{
	m_bPhaseData = bPhaseData;
}

void MainRasterData::clearData()
{
//	if(m_pImg)
//		*m_pImg=0;
	m_pImg = 0;
}

QwtRasterData *MainRasterData::copy() const
{
	return new MainRasterData(*this);
}

QwtDoubleInterval MainRasterData::range() const
{
	if(!m_bAutoRange)
		return QwtDoubleInterval(m_dRange[0], m_dRange[1]);


	if(!m_pImg || !*m_pImg)
	{
		return QwtDoubleInterval(0.,1.);
	}

	double dTmpMax, dTmpMin;
	if(m_bPhaseData)
	{
		dTmpMax=360.;
		dTmpMin=0.;
	}
	else
	{
		dTmpMax = (*m_pImg)->GetDoubleMax();
		dTmpMin = (*m_pImg)->GetDoubleMin();
	}

	if(m_bLog)
	{
		dTmpMax = safe_log10_lowerrange(dTmpMax);
		dTmpMin = safe_log10_lowerrange(dTmpMin);

		if(dTmpMax!=dTmpMax) dTmpMax=0.;
		if(dTmpMin!=dTmpMin) dTmpMin=0.;

		return QwtDoubleInterval(dTmpMin,dTmpMax);
	}
	else
		return QwtDoubleInterval(dTmpMin,dTmpMax);
}

double MainRasterData::value(double x, double y) const
{
	if(!m_pImg || !*m_pImg)
		return 0.;

	double dRet = (*m_pImg)->GetDoubleData((int)x,(int)y);

	if(m_bLog)
		dRet = safe_log10(dRet);

	if(dRet!=dRet) dRet=0.;
	return dRet;
}

double MainRasterData::GetValueRaw(int x, int y) const
{
	if(!m_pImg || !*m_pImg)
		return 0.;

	return (*m_pImg)->GetDoubleData(x,y);
}

void MainRasterData::SetAutoCountRange(bool bAuto)
{ m_bAutoRange = bAuto; }
bool MainRasterData::GetAutoCountRange() const
{ return m_bAutoRange; }

void MainRasterData::SetCountRange(double dMin, double dMax)
{
	SetAutoCountRange(false);

	m_dRange[0] = dMin;
	m_dRange[1] = dMax;
}

// **********************************************************
