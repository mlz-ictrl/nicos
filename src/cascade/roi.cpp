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

#include "roi.h"
#include "helper.h"
#include <math.h>
#include <sstream>


RoiRect::RoiRect(int iX1, int iY1, int iX2, int iY2)
		: m_iX1(iX1), m_iY1(iY1), m_iX2(iX2), m_iY2(iY2)
{
	if(m_iX1 > m_iX2)
		swap(m_iX1, m_iX2);
	if(m_iY1 > m_iY2)
		swap(m_iY1, m_iY2);
}

RoiRect::RoiRect()
	    : m_iX1(0.), m_iY1(0.), m_iX2(0.), m_iY2(0.)
{}

bool RoiRect::IsInside(int iX, int iY) const
{
	if(iX>=m_iX1 && iX<=m_iX2 &&
	   iY>=m_iY1 && iY<=m_iY2)
	   return true;
	return false;
}

std::string RoiRect::GetName() const { return "rectangle"; }

int RoiRect::GetParamCount() const
{
	// 0: m_iX1
	// 1: m_iY1
	// 2: m_iX2
	// 3: m_iY2
	return 4;
}

std::string RoiRect::GetParamName(int iParam) const
{
	std::string strRet;

	switch(iParam)
	{
		case 0: strRet="x1"; break;
		case 1: strRet="y1"; break;
		case 2: strRet="x2"; break;
		case 3: strRet="y2"; break;
		default: strRet="unknown"; break;
	}

	return strRet;
}

double RoiRect::GetParam(int iParam) const
{
	switch(iParam)
	{
		case 0: return m_iX1;
		case 1: return m_iY1;
		case 2: return m_iX2;
		case 3: return m_iY2;
	}
	return 0.;
}

void RoiRect::SetParam(int iParam, double dVal)
{
	switch(iParam)
	{
		case 0: m_iX1 = dVal; break;
		case 1: m_iY1 = dVal; break;
		case 2: m_iX2 = dVal; break;
		case 3: m_iY2 = dVal; break;
	}
}


//------------------------------------------------------------------------------


RoiCircle::RoiCircle(double dCenter[2], double dRadius)
{
	m_dCenter[0] = dCenter[0];
	m_dCenter[1] = dCenter[1];

	m_dRadius = dRadius;
}

RoiCircle::RoiCircle()
{
	m_dCenter[0] = 0.;
	m_dCenter[1] = 0.;

	m_dRadius = 0.;
}

bool RoiCircle::IsInside(int iX, int iY) const
{
	return IsInside(double(iX), double(iY));
}

bool RoiCircle::IsInside(double dX, double dY) const
{
	double dX_0 = dX - m_dCenter[0];
	double dY_0 = dY - m_dCenter[1];

	double dLen = sqrt(dX_0*dX_0 + dY_0*dY_0);
	return dLen <= m_dRadius;
}

std::string RoiCircle::GetName() const { return "circle"; }

int RoiCircle::GetParamCount() const
{
	// 0: m_dCenter[0]
	// 1: m_dCenter[1]
	// 2: m_dRadius
	return 3;
}

std::string RoiCircle::GetParamName(int iParam) const
{
	std::string strRet;

	switch(iParam)
	{
		case 0: strRet="center x"; break;
		case 1: strRet="center y"; break;
		case 2: strRet="radius"; break;
		default: strRet="unknown"; break;
	}

	return strRet;
}

double RoiCircle::GetParam(int iParam) const
{
	switch(iParam)
	{
		case 0: return m_dCenter[0];
		case 1: return m_dCenter[1];
		case 2: return m_dRadius;
	}
	return 0.;
}

void RoiCircle::SetParam(int iParam, double dVal)
{
	switch(iParam)
	{
		case 0: m_dCenter[0] = dVal; break;
		case 1: m_dCenter[1] = dVal; break;
		case 2: m_dRadius = dVal; break;
	}
}


//------------------------------------------------------------------------------


Roi::Roi()
{}

Roi::~Roi()
{
	clear();
}

int Roi::add(RoiElement* elem)
{
	m_vecRoi.push_back(elem);
	return m_vecRoi.size()-1;
}

void Roi::clear()
{
	for(unsigned int i=0; i<m_vecRoi.size(); ++i)
	{
		if(m_vecRoi[i])
		{
			delete m_vecRoi[i];
			m_vecRoi[i] = 0;
		}
	}
	m_vecRoi.clear();
}

bool Roi::IsInside(int iX, int iY) const
{
	for(unsigned int i=0; i<m_vecRoi.size(); ++i)
	{
		if(m_vecRoi[i]->IsInside(iX, iY))
			return true;
	}
	return false;
}

RoiElement& Roi::GetElement(int iElement)
{
	return *m_vecRoi[iElement];
}

void Roi::DeleteElement(int iElement)
{
	if(m_vecRoi[iElement])
		delete m_vecRoi[iElement];
	m_vecRoi.erase(m_vecRoi.begin()+iElement);
}

int Roi::GetNumElements() const
{
	return m_vecRoi.size();
}
