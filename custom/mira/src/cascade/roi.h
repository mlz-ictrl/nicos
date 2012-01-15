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

#ifndef __TOF_ROI__
#define __TOF_ROI__

#include <vector>
#include <string>
#include "vec2d.h"

#define CIRCLE_VERTICES 256


struct BoundingRect
{
	Vec2d<double> bottomleft;
	Vec2d<double> topright;

	void SetInvalidBounds();
	void AddVertex(const Vec2d<double>& vertex);
};


// base class for roi elements (rectangle, circle, ...)
class RoiElement
{
	protected:
		BoundingRect m_boundingrect;
		virtual void CalculateBoundingRect();

		RoiElement();

	public:
		virtual RoiElement& operator=(const RoiElement& elem);
		virtual RoiElement* copy() const = 0;


		// get name of element
		virtual std::string GetName() const = 0;


		// is point (dX, dY) inside roi element?
		virtual bool IsInside(double dX, double dY) const = 0;

		// what fraction (0.0 .. 1.0) of pixel (iX, iY) is inside roi element?
		virtual double HowMuchInside(int iX, int iY) const;


		//----------------------------------------------------------------------
		// vertices of element (interpolated for circles)
		virtual int GetVertexCount() const = 0;
		virtual Vec2d<double> GetVertex(int i) const = 0;
		//----------------------------------------------------------------------


		//----------------------------------------------------------------------
		// parameters
		// how many parameters does the element have?
		virtual int GetParamCount() const = 0;

		// get name of a parameter
		virtual std::string GetParamName(int iParam) const = 0;

		// get value of a parameter
		virtual double GetParam(int iParam) const = 0;

		// set value of a parameter
		virtual void SetParam(int iParam, double dVal) = 0;
		//----------------------------------------------------------------------

		// bounding rect for the element's current parameters
		virtual const BoundingRect& GetBoundingRect() const;

		// is point (iX, iY) inside elementzy
		virtual bool IsInBoundingRect(double dX, double dY) const;
};


class RoiRect : public RoiElement
{
	protected:
		Vec2d<double> m_bottomleft, m_topright;
		double m_dAngle;

	public:
		RoiRect(double dX1, double dY1, double dX2, double dY2, double dAngle=0.);
		RoiRect(const Vec2d<double>& bottomleft,
				const Vec2d<double>& topright, double dAngle=0.);
		RoiRect();
		RoiRect(const RoiRect& rect);

		virtual bool IsInside(double dX, double dY) const;

		virtual std::string GetName() const;

		virtual int GetParamCount() const;
		virtual std::string GetParamName(int iParam) const;
		virtual double GetParam(int iParam) const;
		virtual void SetParam(int iParam, double dVal);

		virtual int GetVertexCount() const;
		virtual Vec2d<double> GetVertex(int i) const;

		virtual RoiRect& operator=(const RoiRect& elem);
		virtual RoiElement* copy() const;
};


class RoiCircle : public RoiElement
{
	protected:
		Vec2d<double> m_vecCenter;
		double m_dRadius;

		virtual void CalculateBoundingRect();

	public:
		RoiCircle(const Vec2d<double>& vecCenter, double dRadius);
		RoiCircle();
		RoiCircle(const RoiCircle& elem);

		virtual bool IsInside(double dX, double dY) const;

		virtual std::string GetName() const;

		virtual int GetParamCount() const;
		virtual std::string GetParamName(int iParam) const;
		virtual double GetParam(int iParam) const;
		virtual void SetParam(int iParam, double dVal);

		virtual int GetVertexCount() const;
		virtual Vec2d<double> GetVertex(int i) const;

		virtual RoiCircle& operator=(const RoiCircle& elem);
		virtual RoiElement* copy() const;
};


class RoiEllipse : public RoiElement
{
	protected:
		Vec2d<double> m_vecCenter;
		double m_dRadiusX, m_dRadiusY;

		virtual void CalculateBoundingRect();

	public:
		RoiEllipse(const Vec2d<double>& vecCenter,
					double dRadiusX, double dRadiusY);
		RoiEllipse();
		RoiEllipse(const RoiEllipse& elem);

		virtual bool IsInside(double dX, double dY) const;

		virtual std::string GetName() const;

		virtual int GetParamCount() const;
		virtual std::string GetParamName(int iParam) const;
		virtual double GetParam(int iParam) const;
		virtual void SetParam(int iParam, double dVal);

		virtual int GetVertexCount() const;
		virtual Vec2d<double> GetVertex(int i) const;

		virtual RoiEllipse& operator=(const RoiEllipse& elem);
		virtual RoiElement* copy() const;
};


class RoiCircleRing : public RoiElement
{
	protected:
		Vec2d<double> m_vecCenter;
		double m_dInnerRadius, m_dOuterRadius;

		virtual void CalculateBoundingRect();

	public:
		RoiCircleRing(const Vec2d<double>& vecCenter,
					  double dInnerRadius, double dOuterRadius);
		RoiCircleRing();
		RoiCircleRing(const RoiCircleRing& elem);

		virtual bool IsInside(double dX, double dY) const;

		virtual std::string GetName() const;

		virtual int GetParamCount() const;
		virtual std::string GetParamName(int iParam) const;
		virtual double GetParam(int iParam) const;
		virtual void SetParam(int iParam, double dVal);

		virtual int GetVertexCount() const;
		virtual Vec2d<double> GetVertex(int i) const;

		virtual RoiCircleRing& operator=(const RoiCircleRing& elem);
		virtual RoiElement* copy() const;
};


class RoiCircleSegment : public RoiCircleRing
{
	protected:
		double m_dBeginAngle, m_dEndAngle;

		virtual void CalculateBoundingRect();

	public:
		RoiCircleSegment(const Vec2d<double>& vecCenter,
						double dInnerRadius, double dOuterRadius,
						double dBeginAngle, double dEndAngle);
		RoiCircleSegment();
		RoiCircleSegment(const RoiCircleSegment& elem);

		virtual bool IsInside(double dX, double dY) const;

		virtual std::string GetName() const;

		virtual int GetParamCount() const;
		virtual std::string GetParamName(int iParam) const;
		virtual double GetParam(int iParam) const;
		virtual void SetParam(int iParam, double dVal);

		virtual int GetVertexCount() const;
		virtual Vec2d<double> GetVertex(int i) const;

		virtual RoiCircleSegment& operator=(const RoiCircleSegment& elem);
		virtual RoiElement* copy() const;
};



class RoiPolygon : public RoiElement
{
	protected:
		std::vector<Vec2d<double> > m_vertices;

	public:
		RoiPolygon();
		RoiPolygon(const RoiPolygon& elem);

		virtual bool IsInside(double dX, double dY) const;

		virtual std::string GetName() const;

		virtual int GetParamCount() const;
		virtual std::string GetParamName(int iParam) const;
		virtual double GetParam(int iParam) const;
		virtual void SetParam(int iParam, double dVal);

		virtual int GetVertexCount() const;
		virtual Vec2d<double> GetVertex(int i) const;
		void AddVertex(const Vec2d<double>& vertex);

		virtual RoiPolygon& operator=(const RoiPolygon& elem);
		virtual RoiElement* copy() const;
};


//------------------------------------------------------------------------------


class Roi
{
	protected:
		std::vector<RoiElement*> m_vecRoi;

	public:
		Roi();
		Roi(const Roi& roi);
		Roi& operator=(const Roi& roi);

		virtual ~Roi();

		// add element, return position of element
		int add(RoiElement* elem);
		void clear();

		// is point (dX, dY) inside roi?
		bool IsInside(double dX, double dY) const;

		// what fraction (0.0 .. 1.0) of pixel (iX, iY) is inside roi?
		double HowMuchInside(int iX, int iY) const;

		RoiElement& GetElement(int iElement);
		const RoiElement& GetElement(int iElement) const;
		void DeleteElement(int iElement);
		int GetNumElements() const;

		// get total bounding rectangle of all elements
		BoundingRect GetBoundingRect() const;

		bool Load(const char* pcFile);
		bool Save(const char* pcFile);
};

#endif
