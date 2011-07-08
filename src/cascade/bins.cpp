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
// Werte in Bins einordnen

#include "bins.h"

Bins::Bins(int iNumBins, double dMin, double dMax) : m_iNumBins(iNumBins),
		m_dMin(dMin), m_dMax(dMax), m_intervals(iNumBins), m_values(iNumBins)
{
	m_dInterval = (dMax-dMin)/double(iNumBins);

	for(int i=0; i<iNumBins; ++i)
	{
		m_intervals[i] = QwtDoubleInterval(dMin + double(i)*m_dInterval,
										   dMin + (double(i)+1.)*m_dInterval);
	}
}

// Zähler des Bins, in dem dWert liegt, erhöhen
void Bins::Inc(double dWert)
{
	if(dWert!=dWert) return; // NaN ignorieren

	int iBin = int((dWert-m_dMin) / m_dInterval);
	if(iBin<0 || iBin>m_iNumBins) return;

	m_values[iBin] += 1.;
}

double Bins::GetMaxVal() const
{
	double dMax=0.;
	for(int i=0; i<m_iNumBins; ++i)
	{
		if(m_values[i]>dMax) dMax=m_values[i];
	}
	return dMax;
}

// in Qwt-kompatibles Format umwandeln
const QwtArray<QwtDoubleInterval>& Bins::GetIntervals() const
{
	return m_intervals;
}

const QwtArray<double>& Bins::GetValues() const
{
	return m_values;
}
