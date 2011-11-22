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
// Klasse, um die TOF- und PAD-Datentypen mit Qwt zu nutzen

#ifndef __TOFDATA__
#define __TOFDATA__

#include <qwt_plot_spectrogram.h>

#include "globals.h"
#include "tofloader.h"

/*
 * base class for PadData & TofData
 */
class MainRasterData : public QwtRasterData
{
	protected:
		// log10?
		bool m_bLog;
		bool m_bPhaseData;

		// has to be a pointer to a pointer since qwt copies
		// these objects and clearData() wouldn't invalidate
		// the pointer in the copies
		BasicImage** m_pImg;

		bool m_bAutoRange;
		double m_dRange[2];

	public:
		MainRasterData(const QwtDoubleRect& rect);
		MainRasterData();
		MainRasterData(const MainRasterData& data2d);
		virtual ~MainRasterData();

		void SetLog10(bool bLog10);
		bool GetLog10(void) const;


		void SetImage(BasicImage** pImg);
		BasicImage* GetImage();

		void SetPhaseData(bool bPhaseData);	// wegen Achsen-Range
		void clearData();

		virtual QwtRasterData *copy() const;
		virtual QwtDoubleInterval range() const;
		virtual double value(double x, double y) const;

		// get (nonlog) raw value without regard to m_bLog
		double GetValueRaw(int x, int y) const;

		int GetWidth() const;
		int GetHeight() const;

		bool GetAutoCountRange() const;
		void SetAutoCountRange(bool bAuto);
		void SetCountRange(double dMin, double dMax);
};

#endif
