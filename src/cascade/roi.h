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

#ifndef __TOF_ROI__
#define __TOF_ROI__

#include <vector>
#include <string>
#include "vec2d.h"

#define CIRCLE_VERTICES 256

// interface for roi elements (rectangle, circle, ...)
class RoiElement
{
	public:
		virtual RoiElement* copy() const = 0;


		// get name of element
		virtual std::string GetName() const = 0;


		// is point (iX, iY) inside element?
		virtual bool IsInside(int iX, int iY) const = 0;


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
};


class RoiRect : public RoiElement
{
	protected:
		Vec2d<int> m_bottomleft, m_topright;
		double m_dAngle;

	public:
		RoiRect(int iX1, int iY1, int iX2, int iY2, double dAngle=0.);
		RoiRect(const Vec2d<int>& bottomleft,
				const Vec2d<int>& topright, double dAngle=0.);
		RoiRect();

		virtual bool IsInside(int iX, int iY) const;

		virtual std::string GetName() const;

		virtual int GetParamCount() const;
		virtual std::string GetParamName(int iParam) const;
		virtual double GetParam(int iParam) const;
		virtual void SetParam(int iParam, double dVal);

		virtual int GetVertexCount() const;
		virtual Vec2d<double> GetVertex(int i) const;

		virtual RoiElement* copy() const;
};


class RoiCircle : public RoiElement
{
	protected:
		Vec2d<double> m_vecCenter;
		double m_dRadius;

	public:
		RoiCircle(const Vec2d<double>& vecCenter, double dRadius);
		RoiCircle();

		virtual bool IsInside(int iX, int iY) const;
		virtual bool IsInside(double dX, double dY) const;

		virtual std::string GetName() const;

		virtual int GetParamCount() const;
		virtual std::string GetParamName(int iParam) const;
		virtual double GetParam(int iParam) const;
		virtual void SetParam(int iParam, double dVal);

		virtual int GetVertexCount() const;
		virtual Vec2d<double> GetVertex(int i) const;

		virtual RoiElement* copy() const;
};


class RoiEllipse : public RoiElement
{
	protected:
		Vec2d<double> m_vecCenter;
		double m_dRadiusX, m_dRadiusY;

	public:
		RoiEllipse(const Vec2d<double>& vecCenter,
					double dRadiusX, double dRadiusY);
		RoiEllipse();

		virtual bool IsInside(int iX, int iY) const;
		virtual bool IsInside(double dX, double dY) const;

		virtual std::string GetName() const;

		virtual int GetParamCount() const;
		virtual std::string GetParamName(int iParam) const;
		virtual double GetParam(int iParam) const;
		virtual void SetParam(int iParam, double dVal);

		virtual int GetVertexCount() const;
		virtual Vec2d<double> GetVertex(int i) const;

		virtual RoiElement* copy() const;
};


class RoiCircleRing : public RoiElement
{
	protected:
		Vec2d<double> m_vecCenter;
		double m_dInnerRadius, m_dOuterRadius;

	public:
		RoiCircleRing(const Vec2d<double>& vecCenter,
					  double dInnerRadius, double dOuterRadius);
		RoiCircleRing();

		virtual bool IsInside(int iX, int iY) const;
		virtual bool IsInside(double dX, double dY) const;

		virtual std::string GetName() const;

		virtual int GetParamCount() const;
		virtual std::string GetParamName(int iParam) const;
		virtual double GetParam(int iParam) const;
		virtual void SetParam(int iParam, double dVal);

		virtual int GetVertexCount() const;
		virtual Vec2d<double> GetVertex(int i) const;

		virtual RoiElement* copy() const;
};


class RoiCircleSegment : public RoiCircleRing
{
	protected:
		double m_dBeginAngle, m_dEndAngle;

	public:
		RoiCircleSegment(const Vec2d<double>& vecCenter,
						double dInnerRadius, double dOuterRadius,
						double dBeginAngle, double dEndAngle);
		RoiCircleSegment();

		virtual bool IsInside(int iX, int iY) const;
		virtual bool IsInside(double dX, double dY) const;

		virtual std::string GetName() const;

		virtual int GetParamCount() const;
		virtual std::string GetParamName(int iParam) const;
		virtual double GetParam(int iParam) const;
		virtual void SetParam(int iParam, double dVal);

		virtual int GetVertexCount() const;
		virtual Vec2d<double> GetVertex(int i) const;

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

		bool IsInside(int iX, int iY) const;

		RoiElement& GetElement(int iElement);
		const RoiElement& GetElement(int iElement) const;
		void DeleteElement(int iElement);
		int GetNumElements() const;

		bool Load(const char* pcFile);
		bool Save(const char* pcFile);
};

#endif
