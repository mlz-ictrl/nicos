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

// interface for roi elements (rectangle, circle, ...)
class RoiElement
{
	public:
		// is point (iX, iY) inside element?
		virtual bool IsInside(int iX, int iY) const = 0;


		// get description string of element
		virtual std::string GetName() const = 0;

		// how many parameters does the element have?
		virtual int GetParamCount() const = 0;

		// get name of a parameter
		virtual std::string GetParamName(int iParam) const = 0;

		// get value of a parameter
		virtual double GetParam(int iParam) const = 0;

		// set value of a parameter
		virtual void SetParam(int iParam, double dVal) = 0;
};


class RoiRect : public RoiElement
{
	protected:
		int m_iX1, m_iY1, m_iX2, m_iY2;

	public:
		RoiRect(int iX1, int iY1, int iX2, int iY2);
		RoiRect();

		virtual bool IsInside(int iX, int iY) const;

		virtual std::string GetName() const;
		virtual int GetParamCount() const;
		virtual std::string GetParamName(int iParam) const;
		virtual double GetParam(int iParam) const;
		virtual void SetParam(int iParam, double dVal);
};


class RoiCircle : public RoiElement
{
	protected:
		double m_dCenter[2];
		double m_dRadius;

	public:
		RoiCircle(double dCenter[2], double dRadius);
		RoiCircle();

		virtual bool IsInside(int iX, int iY) const;
		virtual bool IsInside(double dX, double dY) const;

		virtual std::string GetName() const;
		virtual int GetParamCount() const;
		virtual std::string GetParamName(int iParam) const;
		virtual double GetParam(int iParam) const;
		virtual void SetParam(int iParam, double dVal);
};


//------------------------------------------------------------------------------


class Roi
{
	protected:
		std::vector<RoiElement*> m_vecRoi;

	public:
		Roi();
		virtual ~Roi();

		void add(RoiElement* elem);
		void clear();

		bool IsInside(int iX, int iY) const;

		RoiElement& GetElement(int iElement);
		int GetNumElements() const;
};

#endif
