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

#ifndef __FOURIER__
#define __FOURIER__

#include <complex>


//------------------------------------------------------------------------------
// standard dft
// dft formulas from here:
// http://www.fftw.org/fftw3_doc/The-1d-Discrete-Fourier-Transform-_0028DFT_0029.html#The-1d-Discrete-Fourier-Transform-_0028DFT_0029

/**
 * calculate one coefficient of the dft
 * \param k coefficient number
 * \param pReal real input data
 * \param pImag imaginary input data
 * \param n size of data arrays
 * \return fourier coefficient
 */
template<typename T>
std::complex<T> dft_coeff(int k,
					const T *pReal, const T *pImag,
					unsigned int n)
{
	std::complex<T> imag(0., 1.);

	std::complex<T> f(0.,0.);
	for(unsigned int j=0; j<n; ++j)
	{
		std::complex<T> t(pReal?pReal[j]:T(0), pImag?pImag[j]:T(0));

		T dv = -2.*M_PI*T(j)*T(k)/T(n);
		f += t * (cos(dv) + imag*sin(dv));
	}

	return f;
}

/**
 * calculate the discrete fourier transform
 * \param pRealIn real input data
 * \param pImagIn imaginary input data
 * \param pRealOut real output data
 * \param pImagOut imaginary output data
 * \param n size of data arrays
 */
template<typename T>
void dft(const T *pRealIn, const T *pImagIn,
			   T *pRealOut, T *pImagOut, unsigned int n)
{
	for(unsigned int k=0; k<n; ++k)
	{
		std::complex<T> f = dft_coeff<T>(k, pRealIn, pImagIn, n);
		pRealOut[k] = f.real();
		pImagOut[k] = f.imag();
	}
}

/**
 * calculate one coefficient of the inverse dft
 * \param k coefficient number
 * \param pReal real input data
 * \param pImag imaginary input data
 * \param n size of data arrays
 * \return fourier coefficient
 */
template<typename T>
std::complex<T> idft_coeff(int k,
					const T *pReal, const T *pImag,
					unsigned int n)
{
	std::complex<T> imag(0., 1.);

	std::complex<T> t(0.,0.);
	for(unsigned int j=0; j<n; ++j)
	{
		std::complex<T> f(pReal?pReal[j]:T(0), pImag?pImag[j]:T(0));

		T dv = 2.*M_PI*T(j)*T(k)/T(n);
		t += f * (cos(dv) + imag*sin(dv));
	}

	return t;
}

/**
 * calculate the inverse discrete fourier transform
 * \param pRealIn real input data
 * \param pImagIn imaginary input data
 * \param pRealOut real output data
 * \param pImagOut imaginary output data
 * \param n size of data arrays
 */
template<typename T>
void idft(const T *pRealIn, const T *pImagIn,
				T *pRealOut, T *pImagOut, unsigned int n)
{
	for(unsigned int k=0; k<n; ++k)
	{
		std::complex<T> t = idft_coeff<T>(k, pRealIn, pImagIn, n);
		pRealOut[k] = t.real();
		pImagOut[k] = t.imag();
	}
}
//------------------------------------------------------------------------------


//------------------------------------------------------------------------------
// algorithms
/**
 * perform a zero-order phase correction;
 * for a description (albeit in the context of NMR) see e.g. here:
 * http://www-keeler.ch.cam.ac.uk/lectures/Irvine/chapter4.pdf
 */
template<typename T>
std::complex<T> phase_correction_0(const std::complex<T>& c, T dPhase)
{
	return c * std::complex<T>(cos(-dPhase), sin(-dPhase));
}

/**
 * perform a first-order phase correction:
 * dPhase = dPhaseOffs + x*dPhaseSlope
 */
template<typename T>
std::complex<T> phase_correction_1(const std::complex<T>& c,
								T dPhaseOffs, T dPhaseSlope, T x)
{
	return phase_correction_0<T>(c, dPhaseOffs + x*dPhaseSlope);
}
//------------------------------------------------------------------------------


//------------------------------------------------------------------------------
/**
 * \brief fft using fftw
 */
class Fourier
{
	protected:
		unsigned int m_iSize;
		void *m_pIn, *m_pOut;
		void *m_pPlan, *m_pPlan_inv;

		void init_buffers();
		void deinit_buffers();

		double *m_pBufRealIn, *m_pBufRealOut;
		double *m_pBufImgIn, *m_pBufImgOut;

	public:
		/// \param iSize size of data arrays
		Fourier(unsigned int iSize);
		virtual ~Fourier();

		bool fft(const double* pRealIn, const double *pImagIn,
									double *pRealOut, double *pImagOut);
		bool ifft(const double* pRealIn, const double *pImagIn,
									double *pRealOut, double *pImagOut);

		/// same as phase_correction_0 only with one frequency shifted and
		/// all others filtered out
		bool shift_sin(double dNumOsc, const double* pDatIn,
						double *pDataOut, double dPhase);

		/**
		 * shift a sine given in pDatIn by dPhase
		 * we cannot phase shift a sine directly in the time domain due to
		 * binning constraints; but in the frequency domain the phase is
		 * a continuous variable which we can arbitrarily change and then
		 * transform the data back into the time domain to get a shifted rebinning
		 */
		bool phase_correction_0(double dNumOsc, const double* pDatIn,
						double *pDataOut, double dPhase);

		bool phase_correction_1(double dNumOsc, const double* pDatIn,
						double *pDataOut, double dPhaseOffs, double dPhaseSlope);

		/// calculate MIEZE contrast & phase
		bool get_contrast(double dNumOsc, const double* pDatIn,
						  double& dC, double& dPh);
};
//------------------------------------------------------------------------------

#endif
