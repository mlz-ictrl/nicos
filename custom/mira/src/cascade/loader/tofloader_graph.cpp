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

TmpGraph::TmpGraph(const TofConfig* pTofConf) :
			m_iW(0), m_puiDaten(0)
{
	if(pTofConf)
		m_TofConfig = *pTofConf;
	else
		m_TofConfig = GlobalConfig::GetTofConfig();
}

TmpGraph::~TmpGraph()
{
	if(m_puiDaten)
	{
		gc.release(m_puiDaten);
		m_puiDaten=NULL;
	}
}

TmpGraph::TmpGraph(const TmpGraph& tmp)
{
	operator=(const_cast<TmpGraph&>(tmp));
}

TmpGraph& TmpGraph::operator=(const TmpGraph& tmp)
{
	m_iW = tmp.m_iW;
	m_puiDaten = tmp.m_puiDaten;
	m_TofConfig = tmp.m_TofConfig;
	gc.acquire(m_puiDaten);

	return *this;
}

unsigned int TmpGraph::GetData(int iX) const
{
	if(!m_puiDaten) return 0;
	if(iX>=0 && iX<m_iW)
		return m_puiDaten[iX];
	return 0;
}

int TmpGraph::GetWidth(void) const { return m_iW; }

int TmpGraph::GetMin() const
{
	if(!m_puiDaten) return 0;

	unsigned int uiMin = std::numeric_limits<int>::max();
	for(int i=0; i<m_iW; ++i)
		if(m_puiDaten[i]<uiMin) uiMin = m_puiDaten[i];
	return uiMin;
}

int TmpGraph::GetMax() const
{
	if(!m_puiDaten) return 0;

	unsigned int uiMax = 0;
	for(int i=0; i<m_iW; ++i)
		if(m_puiDaten[i]>uiMax) uiMax = m_puiDaten[i];
	return uiMax;
}

bool TmpGraph::IsLowerThan(unsigned int iTotal) const
{
	unsigned int iSum=0;
	for(int i=0; i<m_iW; ++i)
		iSum += GetData(i);

	return iSum < iTotal;
}

bool TmpGraph::FitSinus(double &dFreq, double &dPhase, double &dAmp, double &dOffs,
						double &dPhase_err, double &dAmp_err, double &dOffs_err) const
{
	dFreq = dPhase = dAmp = dOffs = dPhase_err = dAmp_err = dOffs_err = 0.;

	if(m_iW<=0 || IsLowerThan(GlobalConfig::GetMinCountsToFit()))
		return false;

	double dNumOsc = m_TofConfig.GetNumOscillations();

	// Freq fix
	dFreq = dNumOsc * 2.*M_PI/double(m_iW);

	bool bFitOk = ::FitSinus(m_iW, m_puiDaten, dFreq,
							dPhase, dAmp, dOffs,
							dPhase_err, dAmp_err, dOffs_err);

	return bFitOk;
}

bool TmpGraph::FitSinus(double& dFreq, double &dPhase, double &dAmp, double &dOffs) const
{
	double dPhase_err, dAmp_err, dOffs_err;

	return FitSinus(dFreq, dPhase, dAmp, dOffs,
					dPhase_err, dAmp_err, dOffs_err);
}

bool TmpGraph::CalcContrast(double dAmp, double dOffs,
						double dAmp_err, double dOffs_err,
						double &dContrast, double &dContrast_err)
{
	dContrast = dAmp / dOffs;
	dContrast_err = sqrt((1/dOffs*dAmp_err)*(1/dOffs*dAmp_err)
					+ (-dAmp/(dOffs*dOffs)*dOffs_err)*(-dAmp/(dOffs*dOffs)*dOffs_err));

	if(dContrast != dContrast)
	{
		dContrast = 0.;
		return false;
	}
	return true;
}

bool TmpGraph::GetContrast(double &dContrast, double &dPhase,
							double &dContrast_err, double &dPhase_err,
							const TmpGraph* punderground, double dMult_ug) const
{
	dContrast = dContrast_err = 0.;
	dPhase = dPhase_err = 0.;

	double dFreq = 0.;
	double dAmp = 0., dOffs = 0.;
	double dAmp_err = 0., dOffs_err = 0.;

	if(!FitSinus(dFreq, dPhase, dAmp, dOffs, dPhase_err, dAmp_err, dOffs_err))
		return false;

	if(!punderground)
	{
		if(!CalcContrast(dAmp, dOffs, dAmp_err, dOffs_err,
					 dContrast, dContrast_err))
			return false;
	}
	else
	{
		double dFreq_ug;
		double dAmp_ug, dOffs_ug;
		double dAmp_err_ug, dOffs_err_ug;
		double dPhase_ug, dPhase_err_ug;

		if(!punderground->FitSinus(dFreq_ug, dPhase_ug, dAmp_ug, dOffs_ug,
									dPhase_err_ug, dAmp_err_ug, dOffs_err_ug))
			return false;

		dContrast = (dAmp - dMult_ug*dAmp_ug) / (dOffs - dMult_ug*dOffs_ug);

		double A = dAmp;
		double O = dOffs;
		double Au = dAmp_ug;
		double Ou = dOffs_ug;

		double dA = dAmp_err;
		double dO = dOffs_err;
		double dAu = dAmp_err_ug;
		double dOu = dOffs_err_ug;

		double m = dMult_ug;

		dContrast_err = sqrt(pow(dA/(O-m*Ou), 2.) +
						pow(-(m*dAu)/(O-m*Ou), 2.) +
						pow(-dO*(A-m*Au)/((O-m*Ou)*(O-m*Ou)), 2.) +
						pow(-dOu*(m*m*Au - m*A)/((O-m*Ou)*(O-m*Ou)), 2.));
	}

	//if(dContrast < 0.) dContrast=0.;
	if(dContrast != dContrast)
	{
		dContrast = 0.;
		return false;
	}
	
	return true;
}

bool TmpGraph::GetContrast(double &dContrast, double &dPhase) const
{
	double dContrast_err, dPhase_err;
	return GetContrast(dContrast, dPhase, dContrast_err, dPhase_err);
}

unsigned int TmpGraph::Sum(void) const
{
	unsigned int uiSum = 0;

	for(int i=0; i<m_iW; ++i)
		uiSum += GetData(i);

	return uiSum;
}

bool TmpGraph::Save(const char* pcFile) const
{
	std::ofstream ofstr(pcFile);
	if(!ofstr.is_open())
		return false;

	for(int i=0; i<m_iW; ++i)
	{
		ofstr << i << "\t" << m_puiDaten[i];
		ofstr << "\n";
	}

	ofstr.close();
	return true;
}
