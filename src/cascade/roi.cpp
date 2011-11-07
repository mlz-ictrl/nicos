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

#include <math.h>
#include <sstream>
#include <fstream>

#include "roi.h"
#include "helper.h"
#include "config.h"
#include "logger.h"


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


RoiElement* RoiRect::copy() const
{
	return new RoiRect(m_iX1, m_iY1, m_iX2, m_iY2);
}


//------------------------------------------------------------------------------


RoiCircle::RoiCircle(const double dCenter[2], double dRadius)
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
		case 0: strRet="center_x"; break;
		case 1: strRet="center_y"; break;
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

RoiElement* RoiCircle::copy() const
{
	return new RoiCircle(m_dCenter, m_dRadius);
}

//------------------------------------------------------------------------------


Roi::Roi()
{}

Roi::Roi(const Roi& roi)
{
	operator=(roi);
}

Roi& Roi::operator=(const Roi& roi)
{
	for(int i=0; i<roi.GetNumElements(); ++i)
	{
		const RoiElement& elem = roi.GetElement(i);

		RoiElement* pNewElem = elem.copy();
		add(pNewElem);
	}
	return *this;
}

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

const RoiElement& Roi::GetElement(int iElement) const
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

bool Roi::Load(const char* pcFile)
{
	clear();

	Config xml;
	if(!xml.Load(pcFile))
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Roi: Cannot load \"" << pcFile << "\".\n";

		return false;
	}

	for(int iElem=0; true; ++iElem)
	{
		std::ostringstream ostr;
		ostr << "/roi_elements/element_";
		ostr << iElem;
		ostr << "/";

		std::string strQueryBase = ostr.str();
		std::string strQueryType = strQueryBase + std::string("type");

		bool bOK=false;
		std::string strType = xml.QueryString(strQueryType.c_str(), "", &bOK);
		if(!bOK)
			break;

		RoiElement *pElem = 0;
		if(strType == std::string("rectangle"))
			pElem = new RoiRect;
		else if(strType == std::string("circle"))
			pElem = new RoiCircle;
		else
		{
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "Roi: Unknown element \"" << strType << "\".\n";
			continue;
		}

		for(int iParam=0; iParam<pElem->GetParamCount(); ++iParam)
		{
			std::string strQueryParam = pElem->GetParamName(iParam);
			double dVal = xml.QueryDouble((strQueryBase + strQueryParam).c_str());

			pElem->SetParam(iParam, dVal);
		}

		add(pElem);
	}
	return true;
}

bool Roi::Save(const char* pcFile)
{
	std::ofstream ofstr(pcFile);
	if(!ofstr.is_open())
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Roi: Cannot save \"" << pcFile << "\".\n";

		return false;
	}

	ofstr << "<?xml version=\"1.0\"?>\n\n";
	ofstr << "<!-- ROI element configuration for Cascade Viewer -->\n\n";
	ofstr << "<roi_elements>\n\n";

	for(int i=0; i<GetNumElements(); ++i)
	{
		RoiElement& elem = GetElement(i);
		ofstr << "\t<element_" << i << ">\n";
		ofstr << "\t\t<type>" << elem.GetName() << "</type>\n";

		for(int iParam=0; iParam<elem.GetParamCount(); ++iParam)
		{
			std::string strParam = elem.GetParamName(iParam);
			double dValue = elem.GetParam(iParam);

			ofstr << "\t\t<" << strParam << "> ";
			ofstr << dValue;
			ofstr << " </" << strParam << ">\n";
		}

		ofstr << "\t</element_" << i << ">\n\n";
	}

	ofstr << "</roi_elements>\n";
	ofstr.close();

	return true;
}
