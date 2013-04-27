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

#include "../config/globals.h"
#include "fit.h"
#include "logger.h"
#include "gc.h"
#include "fourier.h"

#ifdef USE_MINUIT
	#include <Minuit2/FCNBase.h>
	#include <Minuit2/FunctionMinimum.h>
	#include <Minuit2/MnMigrad.h>
	#include <Minuit2/MnSimplex.h>
	#include <Minuit2/MnMinimize.h>
	#include <Minuit2/MnFumiliMinimize.h>
	#include <Minuit2/MnUserParameters.h>
	#include <Minuit2/MnPrint.h>
#endif

#include <limits>
#include <math.h>
#include <algorithm>


inline static ROOT::Minuit2::MnApplication* make_minimizer(ROOT::Minuit2::FCNBase &fkt,
														   ROOT::Minuit2::MnUserParameters& upar,
														   int iStrategy=-1)
{
	ROOT::Minuit2::MnApplication *pMinimize = 0;

	if(iStrategy < 0)
		iStrategy = GlobalConfig::GetMinuitStrategy();

	switch(GlobalConfig::GetMinuitAlgo())
	{
		case MINUIT_SIMPLEX:
			pMinimize = new ROOT::Minuit2::MnSimplex(fkt, upar, iStrategy);
			break;

		case MINUIT_MINIMIZE:
			pMinimize = new ROOT::Minuit2::MnMinimize(fkt, upar, iStrategy);
			break;

		default:
		case MINUIT_MIGRAD:
			pMinimize = new ROOT::Minuit2::MnMigrad(fkt, upar, iStrategy);
			break;
	}

	return pMinimize;
}


//------------------------------------------------------------------------------
// Sinus fitting

#ifdef USE_MINUIT

// Model Function for sin fit
class Sinus : public ROOT::Minuit2::FCNBase
{
	protected:
		double *m_pdy;			// experimental values
 		double *m_pddy;			// deviations
		int m_iNum;				// number of values

		double m_dfreq;

	public:
		Sinus(double dFreq) : m_pdy(0), m_pddy(0), m_iNum(0),
								m_dfreq(dFreq)
		{}

		void Clear(void)
		{
			if(m_pddy) { gc.release(m_pddy); m_pddy=NULL; }
			if(m_pdy) { gc.release(m_pdy); m_pdy=NULL; }
			m_iNum=0;
		}

		virtual ~Sinus() { Clear(); }

		double chi2(const std::vector<double>& params) const
		{
			double dphase = params[0];
			double damp = params[1];
			double doffs = params[2];
			double dfreq = m_dfreq; // = 2.*M_PI/double(m_iNum);

			double dchi2 = 0.;
			for(int i=0; i<m_iNum; ++i)
			{
				double dAbweichung = m_pddy[i];

				// prevent division by zero
				if(fabs(dAbweichung) < std::numeric_limits<double>::min())
					dAbweichung = std::numeric_limits<double>::min();

				double d = (m_pdy[i] - (damp*sin(double(i)*dfreq +
										dphase)+doffs)) / dAbweichung;
				dchi2 += d*d;
			}
			return dchi2;
		}

		double operator()(const std::vector<double>& params) const
		{
			return chi2(params);
		}

		double Up() const
		{ return 1.; }

		const double* GetValues() const
		{ return m_pdy; }

		const double* GetDeviations() const
		{ return m_pddy; }

		template<class T>
		void SetValues(int iSize, const T* pdy)
		{
			Clear();
			m_iNum = iSize;
			m_pdy = (double*)gc.malloc(sizeof(double)*iSize, "fit_msin_y");
			m_pddy = (double*)gc.malloc(sizeof(double)*iSize, "fit_msin_dy");

			for(int i=0; i<iSize; ++i)
			{
				m_pdy[i] = double(pdy[i]);				// Value
				m_pddy[i] = sqrt(m_pdy[i]);				// Abs Error!
			}
		}
};

bool FitSinus(int iSize, const unsigned int* pData,
			  double dFreq,
			  double &dPhase, double &dAmp, double &dOffs,
			  double &dPhase_err, double &dAmp_err, double &dOffs_err)
{
	if(iSize<=0) return false;

	unsigned int iMax = *std::max_element(pData, pData+iSize),
				 iMin = *std::min_element(pData, pData+iSize);

	if(iMax==iMin)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Fitter: Invalid data for sinus fit." << "\n";
		return false;
	}

	Sinus fkt(dFreq);
	fkt.SetValues(iSize, pData);


	// hints
	const double *pReal = fkt.GetValues();
	double dNumOsc = dFreq/(2.*M_PI/double(iSize));

	std::complex<double> c = dft_coeff<double>(int(dNumOsc), pReal, 0, iSize);
	dPhase = atan2(c.imag(), c.real()) + M_PI/2.;
	dPhase = fmod(dPhase, 2.*M_PI);
	if(dPhase<0.)
		dPhase += 2.*M_PI;

	dAmp = 0.5 * (iMax-iMin);
	dOffs = double(iMin) + dAmp;

	/*std::cout << "fitter hints: dPhase=" << dPhase
			  << ", dAmp=" << dAmp
			  << ", dOffs=" << dOffs << std::endl;*/


	// step 1: limited fit
	ROOT::Minuit2::MnUserParameters upar;
	upar.Add("phase", dPhase, M_PI*0.1);
	upar.Add("amp", dAmp, 0.1*dAmp);
	upar.Add("offs", dOffs, 0.1*dOffs);

	upar.SetLimits("phase", 0., 2.*M_PI);
	upar.SetLimits("amp", 0., double(iMax));
	upar.SetLimits("offs", double(iMin), double(iMax));


	ROOT::Minuit2::MnApplication *pMinimize = make_minimizer(fkt, upar, 0);
	{
		ROOT::Minuit2::FunctionMinimum mini = (*pMinimize)(
										GlobalConfig::GetMinuitMaxFcn(),
										GlobalConfig::GetMinuitTolerance());

		upar.SetValue("phase", mini.UserState().Value("phase"));
		upar.SetError("phase", mini.UserState().Error("phase"));

		upar.SetValue("amp", mini.UserState().Value("amp"));
		upar.SetError("amp", mini.UserState().Error("amp"));

		upar.SetValue("offs", mini.UserState().Value("offs"));
		upar.SetError("offs", mini.UserState().Error("offs"));
	}

	delete pMinimize;


	// step 2: free fit
	upar.RemoveLimits("amp");
	upar.RemoveLimits("offs");
	upar.RemoveLimits("phase");

	pMinimize = make_minimizer(fkt, upar);

	ROOT::Minuit2::FunctionMinimum mini = (*pMinimize)(
									GlobalConfig::GetMinuitMaxFcn(),
									GlobalConfig::GetMinuitTolerance());

	dPhase = mini.UserState().Value("phase");
	dAmp = mini.UserState().Value("amp");
	dOffs = mini.UserState().Value("offs");

	dPhase_err = mini.UserState().Error("phase");
	dAmp_err = mini.UserState().Error("amp");
	dOffs_err = mini.UserState().Error("offs");

	delete pMinimize;



	if(dAmp<0.)
	{
		dAmp = -dAmp;
		dPhase += M_PI;
	}

	// Phasen auf 0..2*Pi einschränken
	dPhase = fmod(dPhase, 2.*M_PI);
	if(dPhase<0.) dPhase += 2.*M_PI;

	if(!mini.IsValid())
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Fitter: Invalid sinus fit." << "\n";
		return false;
	}

	// check for NaN
	if(dPhase!=dPhase || dAmp!=dAmp || dOffs!=dOffs)
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "Fitter: Incorrect sinus fit." << "\n";
		return false;
	}

	/*std::cout << "fit: dPhase=" << dPhase
			  << ", dAmp=" << dAmp
			  << ", dOffs=" << dOffs << std::endl;*/

	return true;
}

#else

bool FitSinus(int iSize, const unsigned int* pData,
			  double dFreq,
			  double &dPhase, double &dAmp, double &dOffs,
			  double &dPhase_err, double &dAmp_err, double &dOffs_err)
{
	logger.SetCurLogLevel(LOGLEVEL_ERR);
	logger << "Fitter: Not compiled with minuit." << "\n";
	return false;
}

#endif //USE_MINUIT

bool FitSinus(int iSize, const unsigned int* pData,
			  double dFreq,
			  double &dPhase, double &dAmp, double &dOffs)
{
	double dPhase_err_dummy, dAmp_err_dummy, dOffs_err_dummy;
	return FitSinus(iSize, pData,
					dFreq,
					dPhase, dAmp, dOffs,
					dPhase_err_dummy, dAmp_err_dummy, dOffs_err_dummy);
}





//------------------------------------------------------------------------------
// 2D Gaussian fitting

#ifdef USE_MINUIT

// Model Function for Gaussian fit
class Gaussian : public ROOT::Minuit2::FCNBase
{
	protected:
		double *m_pdata;
 		double *m_pspread;
		int m_iW, m_iH;

	public:
		Gaussian() : m_pdata(0), m_pspread(0), m_iW(0), m_iH(0)
		{}

		void Clear(void)
		{
			if(m_pdata) { gc.release(m_pdata); m_pdata=NULL; }
			if(m_pspread) { gc.release(m_pspread); m_pspread=NULL; }
			m_iW=m_iH=0;
		}

		virtual ~Gaussian() { Clear(); }

		double GetSpread(int iX, int iY) const
		{
			return m_pspread[iY*m_iW + iX];
		}

		double GetValue(int iX, int iY) const
		{
			return m_pdata[iY*m_iW + iX];
		}

		double chi2(const std::vector<double>& params) const
		{
			double dAmp = params[0];
			double dCenterX = params[1];
			double dCenterY = params[2];
			double dSpreadX = params[3];
			double dSpreadY = params[4];

			double dchi2 = 0.;

			for(int iY=0; iY<m_iH; ++iY)
				for(int iX=0; iX<m_iW; ++iX)
				{
					double dSpread = GetSpread(iX, iY);
					double dVal = GetValue(iX, iY);
					double dX = double(iX);
					double dY = double(iY);

					// force positive spread values
					if(dSpreadX<0. || dSpreadY<0.) return std::numeric_limits<double>::max();

					// force positive amp
					if(dAmp<1.) return std::numeric_limits<double>::max();

					// force positive center
					//if(dCenterX<0. || dCenterY<0.) return std::numeric_limits<double>::max();


					// prevent division by zero
					if(fabs(dSpread) < std::numeric_limits<double>::min())
						dSpread = std::numeric_limits<double>::min();

					if(fabs(dSpreadX) < std::numeric_limits<double>::min())
						dSpreadX = std::numeric_limits<double>::min();

					if(fabs(dSpreadY) < std::numeric_limits<double>::min())
						dSpreadY = std::numeric_limits<double>::min();

					double d = dVal - dAmp *
							   exp(-0.5*(dX-dCenterX)*(dX-dCenterX)/(dSpreadX*dSpreadX)) *
							   exp(-0.5*(dY-dCenterY)*(dY-dCenterY)/(dSpreadY*dSpreadY));

					d /= dSpread;
					dchi2 += d*d;
				}

			return dchi2;
		}

		double operator()(const std::vector<double>& params) const
		{
			return chi2(params);
		}

		double Up() const
		{ return 1.; }

		template<class T>
		void SetValues(int iW, int iH, const T* pdata)
		{
			Clear();
			m_iW = iW;
			m_iH = iH;
			m_pdata = (double*)gc.malloc(sizeof(double)*iW*iH, "fit_gauss_y");
			m_pspread = (double*)gc.malloc(sizeof(double)*iW*iH, "fit_gauss_dy");

			for(int i=0; i<iW*iH; ++i)
			{
				m_pdata[i] = double(pdata[i]);
				m_pspread[i] = sqrt(pdata[i]);		// Abs. Error
			}
		}
};

bool FitGaussian(int iSizeX, int iSizeY,
				 const unsigned int* pData,
				 double &dAmp,
				 double &dCenterX, double &dCenterY,
				 double &dSpreadX, double &dSpreadY)
{
	if(iSizeX<=0 || iSizeY<=0) return false;

	Gaussian fkt;
	fkt.SetValues(iSizeX, iSizeY, pData);

	ROOT::Minuit2::MnUserParameters upar;
	upar.Add("amp", dAmp, 0.1*dAmp);
	upar.Add("center_x", dCenterX, dSpreadX);
	upar.Add("center_y", dCenterY, dSpreadY);
	upar.Add("spread_x", dSpreadX, 0.1*dSpreadX);
	upar.Add("spread_y", dSpreadY, 0.1*dSpreadY);

	ROOT::Minuit2::MnApplication *pMinimize = make_minimizer(fkt, upar);
	ROOT::Minuit2::FunctionMinimum mini = (*pMinimize)(
									GlobalConfig::GetMinuitMaxFcn(),
									GlobalConfig::GetMinuitTolerance());

	dAmp = mini.UserState().Value("amp");
	dCenterX = mini.UserState().Value("center_x");
	dCenterY = mini.UserState().Value("center_y");
	dSpreadX = mini.UserState().Value("spread_x");
	dSpreadY = mini.UserState().Value("spread_y");

	delete pMinimize;
	pMinimize = 0;

	if(!mini.IsValid())
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Fitter: Invalid guassian fit." << "\n";
		return false;
	}

	// check for NaN
	if(dAmp!=dAmp || dCenterX!=dCenterX || dCenterY!=dCenterY ||
					 dSpreadX!=dSpreadX || dSpreadY!=dSpreadY)
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "Fitter: Incorrect guassian fit." << "\n";
		return false;
	}
	return true;
}


#else

bool FitGaussian(int iSizeX, int iSizeY,
				 const unsigned int* pData,
				 double &dAmp,
				 double &dCenterX, double &dCenterY,
				 double &dSpreadX, double &dSpreadY)
{
	logger.SetCurLogLevel(LOGLEVEL_ERR);
	logger << "Fitter: Not compiled with minuit." << "\n";
	return false;
}

#endif
