// *****************************************************************************
// NICOS, the Networked Instrument Control System of the FRM-II
// Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

#ifndef __BASICIMAGE__
#define __BASICIMAGE__

#include "../auxiliary/roi.h"

/**
 * \brief minimal interface for images
 */
class BasicImage
{
	public:
		/// get image width
		virtual int GetWidth() const = 0;
		/// get image height
		virtual int GetHeight() const = 0;

		/// get pixel as double
		virtual double GetDoubleData(int iX, int iY) const = 0;

		/// get pixel as int
		virtual unsigned int GetIntData(int iX, int iY) const = 0;

		/// minimum value as integer
		virtual int GetIntMin() const = 0;
		/// maximum value as integer
		virtual int GetIntMax() const = 0;
		/// minimum value as double
		virtual double GetDoubleMin() const = 0;
		/// maximum value as double
		virtual double GetDoubleMax() const = 0;
};

class Countable
{
	public:
		/// get total counts (in roi if set)
		virtual unsigned int GetCounts() const = 0;
		/// get total counts subtracting counts outside the roi (area-weighted)
		virtual unsigned int GetCountsSubtractBackground() const = 0;

		virtual Roi& GetRoi() = 0;
		/// enable/disable roi
		virtual void UseRoi(bool bUseRoi=true) = 0;
		/// \return is roi in use?
		virtual bool GetUseRoi() const = 0;
};

#endif
