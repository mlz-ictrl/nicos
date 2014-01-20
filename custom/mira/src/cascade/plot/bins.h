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
// Werte in Bins einordnen

#ifndef __BINS__
#define __BINS__

#include <qwt_data.h>
#include <qwt_double_interval.h>

class Bins
{
	protected:
		int m_iNumBins;
		double m_dMin, m_dMax, m_dInterval;
		
		QwtArray<QwtDoubleInterval> m_intervals;
		QwtArray<double> m_values;
		
	public:
		Bins(int iNumBins, double dMin, double dMax);
		
		/// Zähler des Bins, in dem dWert liegt, erhöhen
		void Inc(double dWert);
		double GetMaxVal() const;
		
		/// in Qwt-kompatibles Format umwandeln
		const QwtArray<QwtDoubleInterval>& GetIntervals() const;
		const QwtArray<double>& GetValues() const;
};

#endif
