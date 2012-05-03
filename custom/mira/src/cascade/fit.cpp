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

#include "fit.h"
#include "logger.h"
#include "globals.h"

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

	public:
		Sinus() : m_pdy(0), m_pddy(0), m_iNum(0)
		{}

		void Clear(void)
		{
			if(m_pddy) { delete[] m_pddy; m_pddy=NULL; }
			if(m_pdy) { delete[] m_pdy; m_pdy=NULL; }
			m_iNum=0;
		}

		virtual ~Sinus() { Clear(); }

		double chi2(const std::vector<double>& params) const
		{
			double dphase = params[0];
			double damp = params[1];
			double doffs = params[2];
			double dscale = 2.*M_PI/double(m_iNum);

			// force non-negative amplitude parameter
			if(damp<0.) return std::numeric_limits<double>::max();

			double dchi2 = 0.;
			for(int i=0; i<m_iNum; ++i)
			{
				double dAbweichung = m_pddy[i];

				// prevent division by zero
				if(fabs(dAbweichung) < std::numeric_limits<double>::epsilon())
					dAbweichung = std::numeric_limits<double>::epsilon();

				double d = (m_pdy[i] - (damp*sin(double(i)*dscale +
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
			m_pdy = new double[iSize];
			m_pddy = new double[iSize];

			for(int i=0; i<iSize; ++i)
			{
				m_pdy[i] = T(pdy[i]);				// Value
				m_pddy[i] = 1./sqrt(m_pdy[i]);		// Error
			}
		}
};

bool FitSinus(int iSize, const unsigned int* pData,
			  double &dPhase, /*double &dScale,*/
			  double &dAmp, double &dOffs)
{
	if(iSize<=0) return false;

	Sinus fkt;
	fkt.SetValues(iSize, pData);

	ROOT::Minuit2::MnUserParameters upar;
	upar.Add("phase", M_PI, 0.01);
	upar.Add("amp", dAmp, 1./sqrt(dAmp));
	upar.Add("offset", dOffs, 1./sqrt(dOffs));
	//upar.Add("scale", 2.*M_PI/16., 0.1);		// don't fit this parameter

	ROOT::Minuit2::MnApplication *pMinimize = 0;

	unsigned int uiStrategy = GlobalConfig::GetMinuitStrategy();
	switch(GlobalConfig::GetMinuitAlgo())
	{
		case MINUIT_SIMPLEX:
			pMinimize = new ROOT::Minuit2::MnSimplex(fkt, upar, uiStrategy);
			break;

		case MINUIT_MINIMIZE:
			pMinimize = new ROOT::Minuit2::MnMinimize(fkt, upar, uiStrategy);
			break;

		default:
		case MINUIT_MIGRAD:
			pMinimize = new ROOT::Minuit2::MnMigrad(fkt, upar, uiStrategy);
			break;
	}

	ROOT::Minuit2::FunctionMinimum mini = (*pMinimize)(
									GlobalConfig::GetMinuitMaxFcn(),
									GlobalConfig::GetMinuitTolerance());

	dPhase = mini.UserState().Value("phase");
	dAmp = mini.UserState().Value("amp");
	dOffs = mini.UserState().Value("offset");
	//dScale = mini.UserState().Value("scale");

	delete pMinimize;
	pMinimize = 0;

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
	return true;
}

#else

bool FitSinus(int iSize, const unsigned int* pData,
			  double &dPhase, double &dScale,
			  double &dAmp, double &dOffs)
{
	logger.SetCurLogLevel(LOGLEVEL_ERR);
	logger << "Fitter: Not compiled with minuit." << "\n";
	return false;
}

#endif //USE_MINUIT





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
			if(m_pdata) { delete[] m_pdata; m_pdata=NULL; }
			if(m_pspread) { delete[] m_pspread; m_pspread=NULL; }
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
					if(fabs(dSpread) < std::numeric_limits<double>::epsilon())
						dSpread = std::numeric_limits<double>::epsilon();

					if(fabs(dSpreadX) < std::numeric_limits<double>::epsilon())
						dSpreadX = std::numeric_limits<double>::epsilon();

					if(fabs(dSpreadY) < std::numeric_limits<double>::epsilon())
						dSpreadY = std::numeric_limits<double>::epsilon();

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
			m_pdata = new double[iW*iH];
			m_pspread = new double[iW*iH];

			for(int i=0; i<iW*iH; ++i)
			{
				m_pdata[i] = T(pdata[i]);
				m_pspread[i] = 1./sqrt(pdata[i]);
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
	upar.Add("amp", dAmp, 1./sqrt(dAmp));
	upar.Add("center_x", dCenterX, dSpreadX);
	upar.Add("center_y", dCenterY, dSpreadY);
	upar.Add("spread_x", dSpreadX, 1.);
	upar.Add("spread_y", dSpreadY, 1.);

	ROOT::Minuit2::MnApplication *pMinimize = 0;

	unsigned int uiStrategy = GlobalConfig::GetMinuitStrategy();
	switch(GlobalConfig::GetMinuitAlgo())
	{
		case MINUIT_SIMPLEX:
			pMinimize = new ROOT::Minuit2::MnSimplex(fkt, upar, uiStrategy);
			break;

		case MINUIT_MINIMIZE:
			pMinimize = new ROOT::Minuit2::MnMinimize(fkt, upar, uiStrategy);
			break;

		default:
		case MINUIT_MIGRAD:
			pMinimize = new ROOT::Minuit2::MnMigrad(fkt, upar, uiStrategy);
			break;
	}

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
