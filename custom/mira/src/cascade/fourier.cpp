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

#ifdef USE_FFTW
	#include <fftw3.h>
#endif


#ifdef USE_FFTW

bool fft(int iSize, const double* pRealIn, const double *pImagIn,
					double *pRealOut, double *pImagOut)
{
	fftw_complex *pIn = (fftw_complex*)fftw_malloc(iSize * sizeof(fftw_complex));
	fftw_complex *pOut = (fftw_complex*)fftw_malloc(iSize * sizeof(fftw_complex));

	for(int i=0; i<iSize; ++i)
	{
		pIn[i][0] = pRealIn[i];
		pIn[i][1] = pImagIn[i];

		pOut[i][0] = 0.;
		pOut[i][1] = 0.;
	}

	fftw_plan plan = fftw_plan_dft_1d(iSize, pIn, pOut, FFTW_FORWARD, FFTW_ESTIMATE);
	if(!plan)
		return false;
	
	fftw_execute(plan);

	for(int i=0; i<iSize; ++i)
	{
		pRealOut[i] = pOut[i][0];
		pImagOut[i] = pOut[i][1];
	}

	fftw_destroy_plan(plan);
	fftw_free(pIn);
	fftw_free(pOut);
	
	return true;
}

bool ifft(int iSize, const double* pRealIn, const double *pImagIn,
					double *pRealOut, double *pImagOut)
{
	fftw_complex *pIn = (fftw_complex*)fftw_malloc(iSize * sizeof(fftw_complex));
	fftw_complex *pOut = (fftw_complex*)fftw_malloc(iSize * sizeof(fftw_complex));

	for(int i=0; i<iSize; ++i)
	{
		pIn[i][0] = pRealIn[i];
		pIn[i][1] = pImagIn[i];

		pOut[i][0] = 0.;
		pOut[i][1] = 0.;
	}

	fftw_plan plan = fftw_plan_dft_1d(iSize, pIn, pOut, FFTW_BACKWARD, FFTW_ESTIMATE);
	if(!plan)
		return false;

	fftw_execute(plan);

	for(int i=0; i<iSize; ++i)
	{
		pRealOut[i] = pOut[i][0];
		pImagOut[i] = pOut[i][1];
	}

	fftw_destroy_plan(plan);
	fftw_free(pIn);
	fftw_free(pOut);

	return true;
}

#else	// !USE_FFTW

bool no_fft()
{
	logger.SetCurLogLevel(LOGLEVEL_ERR);
	logger << "Fourier: Not compiled with fftw.\n";

	return false;
}

bool fft(int iSize, const double* pRealIn, const double *pImagIn,
					double *pRealOut, double *pImagOut)
{ return no_fft(); }

bool ifft(int iSize, const double* pRealIn, const double *pImagIn,
					double *pRealOut, double *pImagOut)
{ return no_fft(); }

#endif	// USE_FFTW



bool shift_sin(int iSize, double dNumOsc, const double* pDatIn,
				double *pDataOut, double dPhase)
{
	const double dSize = double(iSize);
	const int iNumOsc = int(dNumOsc);
	dNumOsc = double(iNumOsc);			// consider only full oscillations
	
	double dShiftSamples = dPhase/(2.*M_PI) * dSize;

	double *pZero = new double[iSize];
	memset(pZero, 0, sizeof(double)*iSize);

	double *pDatFFT_real = new double[iSize];
	double *pDatFFT_imag = new double[iSize];

	fft(iSize, pDatIn, pZero, pDatFFT_real, pDatFFT_imag);

	for(int i=0; i<iSize; ++i)
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


	ifft(iSize, pDatFFT_real, pDatFFT_imag, pDataOut, pZero);

	// normalization
	for(int i=0; i<iSize; ++i)
		pDataOut[i] /= double(iSize);


	delete[] pDatFFT_real;
	delete[] pDatFFT_imag;

	delete[] pZero;

	return true;
}

/*
// Test
#include <iostream>
#include <fstream>

int main()
{
	const int N = 64;
	
	double dIn[N];
	double dOut[N];

	for(int i=0; i<N; ++i)
		dIn[i] = sin(2.* double(i+0.5)/double(N) * 2.*M_PI);

	shift_sin(N, 2., dIn, dOut, M_PI);

	std::ofstream ofstr("tst.dat");

	for(int i=0; i<N; ++i)
		ofstr << dOut[i] << "\n";

	ofstr.close();
	return 0;
}
*/
