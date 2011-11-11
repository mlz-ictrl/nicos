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
#include <limits>

#include "roi.h"
#include "helper.h"
#include "config.h"
#include "logger.h"
#include "mat2d.h"
#include "pnpoly.h"

//------------------------------------------------------------------------------
// rect

RoiRect::RoiRect(const Vec2d<int>& bottomleft,
				 const Vec2d<int>& topright, double dAngle)
		: m_bottomleft(bottomleft), m_topright(topright), m_dAngle(dAngle)
{
	if(m_bottomleft[0] > m_topright[0])
		swap(m_bottomleft[0], m_topright[0]);
	if(m_bottomleft[1] > m_topright[1])
		swap(m_bottomleft[1], m_topright[1]);
}

RoiRect::RoiRect(int iX1, int iY1, int iX2, int iY2, double dAngle)
{
	*this = RoiRect(Vec2d<int>(iX1, iY1), Vec2d<int>(iX2, iY2), dAngle);
}

RoiRect::RoiRect() : m_dAngle(0.)
{}

bool RoiRect::IsInside(int iX, int iY) const
{
	Vec2d<double> bottomleft = m_bottomleft.cast<double>();
	Vec2d<double> topright = m_topright.cast<double>();

	Vec2d<double> vecCenter = bottomleft + (topright-bottomleft)*.5;
	Mat2d<double> matRot_inv = Mat2d<double>::rotation(-m_dAngle/180.*M_PI);

	Vec2d<double> vecPoint(iX, iY);
	vecPoint = matRot_inv*(vecPoint-vecCenter) + vecCenter;

	if(vecPoint[0]>=bottomleft[0] && vecPoint[0]<topright[0] &&
	   vecPoint[1]>=bottomleft[1] && vecPoint[1]<topright[1])
	   return true;
	return false;
}

std::string RoiRect::GetName() const { return "rectangle"; }

int RoiRect::GetParamCount() const
{
	return 5;
}

std::string RoiRect::GetParamName(int iParam) const
{
	std::string strRet;

	switch(iParam)
	{
		case 0: strRet="bottomleft_x"; break;
		case 1: strRet="bottomleft_y"; break;
		case 2: strRet="topright_x"; break;
		case 3: strRet="topright_y"; break;
		case 4: strRet="angle"; break;
		default: strRet="unknown"; break;
	}

	return strRet;
}

double RoiRect::GetParam(int iParam) const
{
	switch(iParam)
	{
		case 0: return m_bottomleft[0];
		case 1: return m_bottomleft[1];
		case 2: return m_topright[0];
		case 3: return m_topright[1];
		case 4: return m_dAngle;
	}
	return 0.;
}

void RoiRect::SetParam(int iParam, double dVal)
{
	switch(iParam)
	{
		case 0: m_bottomleft[0] = dVal; break;
		case 1: m_bottomleft[1] = dVal; break;
		case 2: m_topright[0] = dVal; break;
		case 3: m_topright[1] = dVal; break;
		case 4: m_dAngle = dVal; break;
	}
}

int RoiRect::GetVertexCount() const
{
	return 4;
}

Vec2d<double> RoiRect::GetVertex(int i) const
{
	Vec2d<double> topleft(m_bottomleft[0], m_topright[1]);
	Vec2d<double> bottomright(m_topright[0], m_bottomleft[1]);
	Vec2d<double> bottomleft = m_bottomleft.cast<double>();
	Vec2d<double> topright = m_topright.cast<double>();

	Vec2d<double> vecRet;

	switch(i)
	{
		case 0: vecRet = bottomleft; break;
		case 1: vecRet = topleft; break;
		case 2: vecRet = topright; break;
		case 3: vecRet = bottomright; break;
		default: return Vec2d<double>(0,0);
	}

	Vec2d<double> vecCenter = bottomleft + (topright-bottomleft)*.5;
	Mat2d<double> matRot = Mat2d<double>::rotation(m_dAngle / 180. * M_PI);

	vecRet = matRot*(vecRet-vecCenter) + vecCenter;
	return vecRet;
}


RoiElement* RoiRect::copy() const
{
	return new RoiRect(m_bottomleft, m_topright, m_dAngle);
}




//------------------------------------------------------------------------------
// circle

RoiCircle::RoiCircle(const Vec2d<double>& vecCenter, double dRadius)
		 : m_vecCenter(vecCenter), m_dRadius(dRadius)
{}

RoiCircle::RoiCircle() : m_dRadius(0.)
{}

bool RoiCircle::IsInside(int iX, int iY) const
{
	return IsInside(double(iX), double(iY));
}

bool RoiCircle::IsInside(double dX, double dY) const
{
	double dX_0 = dX - m_vecCenter[0];
	double dY_0 = dY - m_vecCenter[1];

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
		case 0: return m_vecCenter[0];
		case 1: return m_vecCenter[1];
		case 2: return m_dRadius;
	}
	return 0.;
}

void RoiCircle::SetParam(int iParam, double dVal)
{
	switch(iParam)
	{
		case 0: m_vecCenter[0] = dVal; break;
		case 1: m_vecCenter[1] = dVal; break;
		case 2: m_dRadius = dVal; break;
	}
}

int RoiCircle::GetVertexCount() const
{
	return CIRCLE_VERTICES;
}

Vec2d<double> RoiCircle::GetVertex(int i) const
{
	double dAngle = 2*M_PI * double(i)/double(GetVertexCount()-1);

	Vec2d<double> vecRet(m_dRadius*cos(dAngle), m_dRadius*sin(dAngle));
	vecRet = vecRet + m_vecCenter;

	return vecRet;
}

RoiElement* RoiCircle::copy() const
{
	return new RoiCircle(m_vecCenter, m_dRadius);
}



//------------------------------------------------------------------------------
// ellipse

RoiEllipse::RoiEllipse(const Vec2d<double>& vecCenter,
					   double dRadiusX, double dRadiusY)
		 : m_vecCenter(vecCenter), m_dRadiusX(dRadiusX), m_dRadiusY(dRadiusY)
{}

RoiEllipse::RoiEllipse() : m_dRadiusX(0.), m_dRadiusY(0.)
{}

bool RoiEllipse::IsInside(int iX, int iY) const
{
	return IsInside(double(iX), double(iY));
}

bool RoiEllipse::IsInside(double dX, double dY) const
{
	Vec2d<double> vecVertex(dX,dY);

	double dX0 = dX - m_vecCenter[0];
	double dY0 = dY - m_vecCenter[1];

	bool bInside = ((dX0*dX0/(m_dRadiusX*m_dRadiusX) +
				     dY0*dY0/(m_dRadiusY*m_dRadiusY)) <= 1.);

	return bInside;
}

std::string RoiEllipse::GetName() const { return "ellipse"; }

int RoiEllipse::GetParamCount() const
{
	// 0: m_dCenter[0]
	// 1: m_dCenter[1]
	// 2: m_dRadiusX
	// 3: m_dRadiusY
	return 4;
}

std::string RoiEllipse::GetParamName(int iParam) const
{
	std::string strRet;

	switch(iParam)
	{
		case 0: strRet="center_x"; break;
		case 1: strRet="center_y"; break;
		case 2: strRet="radius_x"; break;
		case 3: strRet="radius_y"; break;
		default: strRet="unknown"; break;
	}

	return strRet;
}

double RoiEllipse::GetParam(int iParam) const
{
	switch(iParam)
	{
		case 0: return m_vecCenter[0];
		case 1: return m_vecCenter[1];
		case 2: return m_dRadiusX;
		case 3: return m_dRadiusY;
	}
	return 0.;
}

void RoiEllipse::SetParam(int iParam, double dVal)
{
	switch(iParam)
	{
		case 0: m_vecCenter[0] = dVal; break;
		case 1: m_vecCenter[1] = dVal; break;
		case 2: m_dRadiusX = dVal; break;
		case 3: m_dRadiusY = dVal; break;
	}
}

int RoiEllipse::GetVertexCount() const
{
	return CIRCLE_VERTICES;
}

Vec2d<double> RoiEllipse::GetVertex(int i) const
{
	double dAngle = 2*M_PI * double(i)/double(GetVertexCount()-1);

	Vec2d<double> vecRet(m_dRadiusX*cos(dAngle), m_dRadiusY*sin(dAngle));
	vecRet = vecRet + m_vecCenter;

	return vecRet;
}

RoiElement* RoiEllipse::copy() const
{
	return new RoiEllipse(m_vecCenter, m_dRadiusX, m_dRadiusY);
}




//------------------------------------------------------------------------------
// circle ring

RoiCircleRing::RoiCircleRing(const Vec2d<double>& vecCenter,
								   double dInnerRadius, double dOuterRadius)
				: m_vecCenter(vecCenter),
				  m_dInnerRadius(dInnerRadius), m_dOuterRadius(dOuterRadius)
{
	if(m_dOuterRadius < m_dInnerRadius)
		swap(m_dOuterRadius, m_dInnerRadius);
}

RoiCircleRing::RoiCircleRing()
				: m_dInnerRadius(0.), m_dOuterRadius(0.)
{}

bool RoiCircleRing::IsInside(int iX, int iY) const
{
	return IsInside(double(iX), double(iY));
}

bool RoiCircleRing::IsInside(double dX, double dY) const
{
	Vec2d<double> vecVertex(dX,dY);

	double dX0 = dX - m_vecCenter[0];
	double dY0 = dY - m_vecCenter[1];

	// outside inner radius?
	bool bOutsideInnerRad = ((dX0*dX0/(m_dInnerRadius*m_dInnerRadius) +
						      dY0*dY0/(m_dInnerRadius*m_dInnerRadius)) >= 1.);
	if(!bOutsideInnerRad)
		return false;

	// inside outer radius?
	bool bInsideOuterRad = ((dX0*dX0/(m_dOuterRadius*m_dOuterRadius) +
						     dY0*dY0/(m_dOuterRadius*m_dOuterRadius)) <= 1.);
	if(!bInsideOuterRad)
		return false;

	return true;
}

std::string RoiCircleRing::GetName() const
{
	return "circle_ring";
}

int RoiCircleRing::GetParamCount() const
{
	return 4;
}

std::string RoiCircleRing::GetParamName(int iParam) const
{
	std::string strRet;

	switch(iParam)
	{
		case 0: strRet="center_x"; break;
		case 1: strRet="center_y"; break;
		case 2: strRet="inner_radius"; break;
		case 3: strRet="outer_radius"; break;
		default: strRet="unknown"; break;
	}

	return strRet;
}

double RoiCircleRing::GetParam(int iParam) const
{
	switch(iParam)
	{
		case 0: return m_vecCenter[0];
		case 1: return m_vecCenter[1];
		case 2: return m_dInnerRadius;
		case 3: return m_dOuterRadius;
	}
	return 0.;
}

void RoiCircleRing::SetParam(int iParam, double dVal)
{
	switch(iParam)
	{
		case 0: m_vecCenter[0] = dVal; break;
		case 1: m_vecCenter[1] = dVal; break;
		case 2: m_dInnerRadius = dVal; break;
		case 3: m_dOuterRadius = dVal; break;
	}
}

int RoiCircleRing::GetVertexCount() const
{
	return CIRCLE_VERTICES;
}

Vec2d<double> RoiCircleRing::GetVertex(int i) const
{
	Vec2d<double> vecRet;
	const int iVerticesPerArc = (GetVertexCount())/2;
	const double dAngleRange = 2. * M_PI;

	// inner circle
	if(i<iVerticesPerArc)
	{
		double dAngle = dAngleRange*double(i)/double(iVerticesPerArc-1);

		vecRet[0] = m_dInnerRadius*cos(dAngle);
		vecRet[1] = m_dInnerRadius*sin(dAngle);

		vecRet = vecRet + m_vecCenter;
	}
	// outer circle
	else if(i>=iVerticesPerArc)
	{
		const int iIdx = 2*iVerticesPerArc - i - 1;

		double dAngle = dAngleRange*double(iIdx)/double(iVerticesPerArc-1);

		vecRet[0] = m_dOuterRadius*cos(dAngle);
		vecRet[1] = m_dOuterRadius*sin(dAngle);

		vecRet = vecRet + m_vecCenter;
	}

	return vecRet;
}

RoiElement* RoiCircleRing::copy() const
{
	return new RoiCircleRing(m_vecCenter, m_dInnerRadius, m_dOuterRadius);
}



//------------------------------------------------------------------------------
// circle segment

RoiCircleSegment::RoiCircleSegment(const Vec2d<double>& vecCenter,
								   double dInnerRadius, double dOuterRadius,
								   double dBeginAngle, double dEndAngle)
				: RoiCircleRing(vecCenter, dInnerRadius, dOuterRadius),
				  m_dBeginAngle(dBeginAngle), m_dEndAngle(dEndAngle)
{}

RoiCircleSegment::RoiCircleSegment()
				: RoiCircleRing(),
				  m_dBeginAngle(0.), m_dEndAngle(0.)
{}

bool RoiCircleSegment::IsInside(int iX, int iY) const
{
	return IsInside(double(iX), double(iY));
}

#include <errno.h>

bool RoiCircleSegment::IsInside(double dX, double dY) const
{
	if(!RoiCircleRing::IsInside(dX, dY))
		return false;

	// test if point is between the two angles?

	Vec2d<double> vecVertex(dX,dY);
	vecVertex = vecVertex - m_vecCenter;
	//vecVertex.normalize();

	const double dAngle1Rad = m_dBeginAngle / 180. * M_PI;
	const double dAngle2Rad = m_dEndAngle / 180. * M_PI;

	Vec2d<double> vecNormal1;
	vecNormal1[0] = -sin(dAngle1Rad);
	vecNormal1[1] = cos(dAngle1Rad);

	Vec2d<double> vecNormal2;
	vecNormal2[0] = -sin(dAngle2Rad);
	vecNormal2[1] = cos(dAngle2Rad);

	bool bBetweenAngles = false;
	double dDot1 = vecVertex * vecNormal1;
	double dDot2 = vecVertex * vecNormal2;

	if(dDot1>=0. && dDot2<=0.)
		bBetweenAngles=true;

	if(!bBetweenAngles)
		return false;

	return true;
}

std::string RoiCircleSegment::GetName() const
{
	return "circle_segment";
}

int RoiCircleSegment::GetParamCount() const
{
	return 6;
}

std::string RoiCircleSegment::GetParamName(int iParam) const
{
	std::string strRet;

	if(iParam>=0 && iParam<4)
		return RoiCircleRing::GetParamName(iParam);

	switch(iParam)
	{
		case 4: strRet="begin_angle"; break;
		case 5: strRet="end_angle"; break;
		default: strRet="unknown"; break;
	}

	return strRet;
}

double RoiCircleSegment::GetParam(int iParam) const
{
	if(iParam>=0 && iParam<4)
		return RoiCircleRing::GetParam(iParam);

	switch(iParam)
	{
		case 4: return m_dBeginAngle;
		case 5: return m_dEndAngle;
	}
	return 0.;
}

void RoiCircleSegment::SetParam(int iParam, double dVal)
{
	if(iParam>=0 && iParam<4)
		RoiCircleRing::SetParam(iParam, dVal);

	switch(iParam)
	{
		case 4: m_dBeginAngle = dVal; break;
		case 5: m_dEndAngle = dVal; break;
	}
}

int RoiCircleSegment::GetVertexCount() const
{
	return RoiCircleRing::GetVertexCount();
}

Vec2d<double> RoiCircleSegment::GetVertex(int i) const
{
	Vec2d<double> vecRet;
	const int iVerticesPerArc = (GetVertexCount())/2;
	const double dAngleRange = (m_dEndAngle-m_dBeginAngle) / 180. * M_PI;

	// inner circle
	if(i<iVerticesPerArc)
	{
		double dAngle = dAngleRange*double(i)/double(iVerticesPerArc-1);
		dAngle += m_dBeginAngle / 180. * M_PI;

		vecRet[0] = m_dInnerRadius*cos(dAngle);
		vecRet[1] = m_dInnerRadius*sin(dAngle);

		vecRet = vecRet + m_vecCenter;
	}
	// outer circle
	else if(i>=iVerticesPerArc)
	{
		const int iIdx = 2*iVerticesPerArc - i - 1;

		double dAngle = dAngleRange*double(iIdx)/double(iVerticesPerArc-1);
		dAngle += m_dBeginAngle / 180. * M_PI;

		vecRet[0] = m_dOuterRadius*cos(dAngle);
		vecRet[1] = m_dOuterRadius*sin(dAngle);

		vecRet = vecRet + m_vecCenter;
	}

	return vecRet;
}

RoiElement* RoiCircleSegment::copy() const
{
	return new RoiCircleSegment(m_vecCenter,
								m_dInnerRadius, m_dOuterRadius,
								m_dBeginAngle, m_dEndAngle);
}



//------------------------------------------------------------------------------
// polygon

RoiPolygon::RoiPolygon()
{}

bool RoiPolygon::IsInside(int iX, int iY) const
{
	return IsInside(double(iX), double(iY));
}

// Adaptor to use external pnpoly function more efficiently
class RoiPolygonArrayAdaptor
{
	protected:
		const RoiPolygon* m_pPoly;
		int m_iCoord;

	public:
		RoiPolygonArrayAdaptor(const RoiPolygon* pPoly, int iCoord)
					: m_pPoly(pPoly), m_iCoord(iCoord)
		{}

		double operator[](int i) const
		{
			// repeat first vertex
			if(i==m_pPoly->GetVertexCount())
				i=0;

			return m_pPoly->GetVertex(i)[m_iCoord];
		}
};

bool RoiPolygon::IsInside(double dX, double dY) const
{
	const int iVertCnt = GetVertexCount();

	RoiPolygonArrayAdaptor m_adaptor_x(this,0);
	RoiPolygonArrayAdaptor m_adaptor_y(this,1);

	return (pnpoly(iVertCnt+1, m_adaptor_x, m_adaptor_y, dX, dY) != 0);
}

std::string RoiPolygon::GetName() const
{
	return "polygon";
}

int RoiPolygon::GetParamCount() const
{
	return GetVertexCount()*2;
}

std::string RoiPolygon::GetParamName(int iParam) const
{
	int iVertex = iParam/2;
	int iCoord = iParam%2;

	std::ostringstream ostr;
	ostr << "vertex_" << iVertex << "_" << (iCoord==0?"x":"y");

	return ostr.str();
}

double RoiPolygon::GetParam(int iParam) const
{
	int iVertex = iParam/2;
	int iCoord = iParam%2;

	return GetVertex(iVertex)[iCoord];
}

void RoiPolygon::SetParam(int iParam, double dVal)
{
	int iVertex = iParam/2;
	int iCoord = iParam%2;

	if(iVertex < GetVertexCount())
		m_vertices[iVertex][iCoord] = dVal;
	else
	{
		Vec2d<double> vec;
		vec[iCoord] = dVal;
		m_vertices.push_back(vec);
	}
}

int RoiPolygon::GetVertexCount() const
{
	return m_vertices.size();
}

Vec2d<double> RoiPolygon::GetVertex(int i) const
{
	return m_vertices[i];
}

RoiElement* RoiPolygon::copy() const
{
	RoiPolygon *pPoly = new RoiPolygon;
	pPoly->m_vertices = this->m_vertices;
	return pPoly;
}

void RoiPolygon::AddVertex(const Vec2d<double>& vertex)
{
	//std::cout << vertex[0] << " " << vertex[1] << std::endl;
	m_vertices.push_back(vertex);
}



//------------------------------------------------------------------------------
// roi

Roi::Roi()
{}

Roi::Roi(const Roi& roi)
{
	operator=(roi);
}

Roi& Roi::operator=(const Roi& roi)
{
	clear();

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

		bool bUndeterminedParamCount=false;

		RoiElement *pElem = 0;
		if(strType == std::string("rectangle"))
			pElem = new RoiRect;
		else if(strType == std::string("circle"))
			pElem = new RoiCircle;
		else if(strType == std::string("circle_ring"))
			pElem = new RoiCircleRing;
		else if(strType == std::string("circle_segment"))
			pElem = new RoiCircleSegment;
		else if(strType == std::string("ellipse"))
			pElem = new RoiEllipse;
		else if(strType == std::string("polygon"))
		{
			bUndeterminedParamCount = true;
			pElem = new RoiPolygon;
		}
		else
		{
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "Roi: Unknown element \"" << strType << "\".\n";
			continue;
		}

		int iParamCount = pElem->GetParamCount();
		if(bUndeterminedParamCount)
			iParamCount = std::numeric_limits<int>::max();

		for(int iParam=0; iParam<iParamCount; ++iParam)
		{
			bool bOk=false;

			std::string strQueryParam = pElem->GetParamName(iParam);
			double dVal = xml.QueryDouble((strQueryBase + strQueryParam).c_str(),
											0., &bOk);
			if(!bOk)
				break;
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
		ofstr << "\t\t<type> " << elem.GetName() << " </type>\n";

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
