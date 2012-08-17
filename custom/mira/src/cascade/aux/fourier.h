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

#ifndef __FOURIER__
#define __FOURIER__

class Fourier
{
	protected:
		unsigned int m_iSize;
		void *m_pIn, *m_pOut;
		void *m_pPlan, *m_pPlan_inv;

	public:
		Fourier(unsigned int iSize);
		virtual ~Fourier();

		bool fft(const double* pRealIn, const double *pImagIn,
									double *pRealOut, double *pImagOut);
		bool ifft(const double* pRealIn, const double *pImagIn,
									double *pRealOut, double *pImagOut);

		// shift a sine given in pDatIn by dPhase
		bool shift_sin(double dNumOsc, const double* pDatIn,
						double *pDataOut, double dPhase);

		bool get_contrast(double dNumOsc, const double* pDatIn,
						  double& dC, double& dPh);
};

#endif
