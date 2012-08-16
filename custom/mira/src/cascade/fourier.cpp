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

#include "fourier.h"
#include <complex>
#include <math.h>
#include <string.h>
#include "logger.h"
#include "globals.h"
#include "gc.h"
#include "helper.h"

#ifdef USE_FFTW
	#include <fftw3.h>
#endif


#ifdef USE_FFTW

Fourier::Fourier(unsigned int iSize) : m_iSize(iSize)
{
	m_pIn = fftw_malloc(m_iSize * sizeof(fftw_complex));
	m_pOut = fftw_malloc(m_iSize * sizeof(fftw_complex));

	m_pPlan = gc.malloc(sizeof(fftw_plan), "fftw_plan");
	m_pPlan_inv = gc.malloc(sizeof(fftw_plan), "fftw_plan_inv");

	fftw_plan* pPlan = (fftw_plan*) m_pPlan;
	fftw_plan* pPlan_inv = (fftw_plan*) m_pPlan_inv;
	
	*pPlan = fftw_plan_dft_1d(iSize,
								(fftw_complex*)m_pIn, (fftw_complex*)m_pOut,
								FFTW_FORWARD, FFTW_MEASURE);

	*pPlan_inv = fftw_plan_dft_1d(iSize,
								(fftw_complex*)m_pIn, (fftw_complex*)m_pOut,
								FFTW_BACKWARD, FFTW_MEASURE);

	if(!*pPlan || !*pPlan_inv)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Fourier: Could not create plan.\n";
	}
}

Fourier::~Fourier()
{
	fftw_destroy_plan(*(fftw_plan*)m_pPlan);
	fftw_destroy_plan(*(fftw_plan*)m_pPlan_inv);

	fftw_free(m_pIn);
	fftw_free(m_pOut);
}

bool Fourier::fft(const double* pRealIn, const double *pImagIn,
					double *pRealOut, double *pImagOut)
{
	fftw_plan* pPlan = (fftw_plan*) m_pPlan;
	
	fftw_complex* pIn = (fftw_complex*)m_pIn;
	fftw_complex* pOut = (fftw_complex*)m_pOut;
	
	for(unsigned int i=0; i<m_iSize; ++i)
	{
		pIn[i][0] = pRealIn[i];
		pIn[i][1] = pImagIn[i];

		pOut[i][0] = 0.;
		pOut[i][1] = 0.;
	}	
	
	fftw_execute(*pPlan);

	for(unsigned int i=0; i<m_iSize; ++i)
	{
		pRealOut[i] = pOut[i][0];
		pImagOut[i] = pOut[i][1];
	}

	return true;
}

bool Fourier::ifft(const double* pRealIn, const double *pImagIn,
					double *pRealOut, double *pImagOut)
{
	fftw_plan* pPlan_inv = (fftw_plan*) m_pPlan_inv;
	
	fftw_complex* pIn = (fftw_complex*)m_pIn;
	fftw_complex* pOut = (fftw_complex*)m_pOut;

	for(unsigned int i=0; i<m_iSize; ++i)
	{
		pIn[i][0] = pRealIn[i];
		pIn[i][1] = pImagIn[i];

		pOut[i][0] = 0.;
		pOut[i][1] = 0.;
	}

	fftw_execute(*pPlan_inv);

	for(unsigned int i=0; i<m_iSize; ++i)
	{
		pRealOut[i] = pOut[i][0];
		pImagOut[i] = pOut[i][1];
	}

	return true;
}

#else	// !USE_FFTW

Fourier::Fourier(unsigned int iSize) : m_iSize(iSize)
{
	logger.SetCurLogLevel(LOGLEVEL_ERR);
	logger << "Fourier: Not compiled with fftw.\n";
}

Fourier::~Fourier()
{}

bool Fourier::fft(const double* pRealIn, const double *pImagIn,
					double *pRealOut, double *pImagOut)
{ return false; }

bool Fourier::ifft(const double* pRealIn, const double *pImagIn,
					double *pRealOut, double *pImagOut)
{ return false; }

#endif	// USE_FFTW


bool Fourier::shift_sin(double dNumOsc, const double* pDatIn,
				double *pDataOut, double dPhase)
{
	unsigned int iSize = m_iSize;
	const double dSize = double(iSize);
	const int iNumOsc = int(dNumOsc);
	dNumOsc = double(iNumOsc);			// consider only full oscillations
	
	double dShiftSamples = dPhase/(2.*M_PI) * dSize;

	double *pZero = new double[iSize];
	memset(pZero, 0, sizeof(double)*iSize);

	double *pDatFFT_real = new double[iSize];
	double *pDatFFT_imag = new double[iSize];

	autodeleter<double> _a0(pZero, true);
	autodeleter<double> _a1(pDatFFT_real, true);
	autodeleter<double> _a2(pDatFFT_imag, true);

	if(!fft(pDatIn, pZero, pDatFFT_real, pDatFFT_imag))
		return false;

	for(unsigned int i=0; i<iSize; ++i)
	{
		if(i==iNumOsc) continue;

		pDatFFT_real[i] = 0.;
		pDatFFT_imag[i] = 0.;		
	}

	std::complex<double> c(pDatFFT_real[iNumOsc], pDatFFT_imag[iNumOsc]);
	c *= 2.;
	double dMult = -2.*M_PI/dSize * dShiftSamples;
	c *= std::complex<double>(cos(dMult), sin(dMult));

	pDatFFT_real[iNumOsc] = c.real();
	pDatFFT_imag[iNumOsc] = c.imag();


	if(!ifft(pDatFFT_real, pDatFFT_imag, pDataOut, pZero))
		return false;

	// normalization
	for(unsigned int i=0; i<iSize; ++i)
		pDataOut[i] /= double(iSize);


	return true;
}


/*
// Test
#include <iostream>
#include <fstream>

int main()
{
	const int N = 64;
	Fourier fourier(N);
	
	double dIn[N];
	double dOut[N];

	for(int i=0; i<N; ++i)
		dIn[i] = sin(2.* double(i+0.5)/double(N) * 2.*M_PI);

	fourier.shift_sin(2., dIn, dOut, M_PI);

	for(int i=0; i<N; ++i)
		std::cout << dOut[i] << " ";
	std::cout << std::endl;
	
	return 0;
}
*/
