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

TmpImage::TmpImage(const TofConfig* pTofConf) :
						m_iW(GlobalConfig::GetTofConfig().GetImageWidth()),
						m_iH(GlobalConfig::GetTofConfig().GetImageHeight()),
						m_puiDaten(NULL), m_pdDaten(NULL),
						m_dMin(0), m_dMax(0)
{
	if(pTofConf)
		m_TofConfig = *pTofConf;
	else
		m_TofConfig = GlobalConfig::GetTofConfig();
}

TmpImage::TmpImage(const TmpImage& tmp)
{
	operator=(tmp);
}

TmpImage& TmpImage::operator=(const TmpImage& tmp)
{
	m_iW = tmp.m_iW;
	m_iH = tmp.m_iH;
	m_dMin = tmp.m_dMin;
	m_dMax = tmp.m_dMax;
	m_puiDaten = tmp.m_puiDaten;
	m_pdDaten = tmp.m_pdDaten;
	m_TofConfig = tmp.m_TofConfig;

	gc.acquire(m_puiDaten);
	gc.acquire(m_pdDaten);

	return *this;
}

void TmpImage::Clear(void)
{
	gc.release(m_puiDaten);
	m_puiDaten=NULL;

	gc.release(m_pdDaten);
	m_pdDaten=NULL;
}

TmpImage::~TmpImage() { Clear(); }

double TmpImage::GetData(int iX, int iY) const
{
	return GetDoubleData(iX, iY);
}

unsigned int TmpImage::GetIntData(int iX, int iY) const
{
	if(iX>=0 && iX<m_iW && iY>=0 && iY<m_iH)
	{
		if(m_puiDaten)
			return m_puiDaten[iY*m_iW + iX];
		else if(m_pdDaten)
			return (unsigned int)(m_pdDaten[iY*m_iW + iX]);
	}
	return 0;
}

double TmpImage::GetDoubleData(int iX, int iY) const
{
	if(iX>=0 && iX<m_iW && iY>=0 && iY<m_iH)
	{
		if(m_puiDaten)
			return double(m_puiDaten[iY*m_iW + iX]);
		else if(m_pdDaten)
			return m_pdDaten[iY*m_iW + iX];
	}
	return 0.;
}

int TmpImage::GetWidth() const { return m_iW; }
int TmpImage::GetHeight() const { return m_iH; }

void TmpImage::Add(const TmpImage& tmp)
{
	if(this->m_iH!=tmp.m_iH || this->m_iW!=tmp.m_iW)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Trying to sum incompatible images"
				  " (line " << __LINE__ << ")!\n";
		return;
	}

	for(int iY=0; iY<m_iH; ++iY)
	{
		for(int iX=0; iX<m_iW; ++iX)
		{
			if(m_puiDaten)
			{
				m_puiDaten[iY*m_iW + iX] += (unsigned int)tmp.GetData(iX,iY);
			}
			else if(m_pdDaten)
			{
				m_pdDaten[iY*m_iW + iX] += tmp.GetData(iX,iY);
			}
		}
	}
}

void TmpImage::UpdateRange()
{
	if(!m_puiDaten && !m_pdDaten) return;

	m_dMin=std::numeric_limits<double>::max();
	m_dMax=0;

	for(int iY=0; iY<m_iH; ++iY)
	{
		for(int iX=0; iX<m_iW; ++iX)
		{
			if(m_puiDaten)
			{
				unsigned int uiVal = m_puiDaten[m_iW*iY+iX];

				if(m_dMax < uiVal)
				{
					m_vecMax[0] = iX;
					m_vecMax[1] = iY;
				}

				m_dMin = min(m_dMin, double(uiVal));
				m_dMax = max(m_dMax, double(uiVal));
			}
			else if(m_pdDaten)
			{
				double dVal = m_pdDaten[m_iW*iY+iX];

				if(m_dMax < dVal)
				{
					m_vecMax[0] = iX;
					m_vecMax[1] = iY;
				}

				m_dMin = min(m_dMin, dVal);
				m_dMax = max(m_dMax, dVal);
			}
		}
	}
}

int TmpImage::GetIntMin(void) const { return int(GetDoubleMin()); }
int TmpImage::GetIntMax(void) const { return int(GetDoubleMax()); }
double TmpImage::GetDoubleMin(void) const { return m_dMin; }
double TmpImage::GetDoubleMax(void) const { return m_dMax; }

bool TmpImage::WriteXML(const char* pcFileName,
						int iSampleDetector, double dWavelength,
						double dLifetime, int iBeamMonitor) const
{
	std::ofstream ofstr(pcFileName);
	if(!ofstr.is_open())
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not open file \""
			   << pcFileName << "\" for writing.\n";
		return false;
	}

	ofstr << "<measurement_file>\n\n";
	ofstr << "<instrument_name>MIRA</instrument_name>\n";
	ofstr << "<location>Forschungsreaktor Muenchen II - FRM2</location>\n";

	const int iRes = 1024;

	ofstr << "\n<measurement_data>\n";

	ofstr << "<Sample_Detector>" << iSampleDetector << "</Sample_Detector>\n";
	ofstr << "<wavelength>" << std::setprecision(2) << dWavelength << "</wavelength>\n";
	ofstr << "<lifetime>" << std::setprecision(3) << dLifetime << "</lifetime>\n";
	ofstr << "<beam_monitor>" << iBeamMonitor << "</beam_monitor>\n";
	ofstr << "<resolution>" << iRes << "</resolution>\n";

	ofstr << "\n<detector_value>\n";

	if(iRes % m_iW || iRes % m_iH)
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "Loader: Resolution does not match.\n";
	}

	for(int iX=0; iX<m_iW; ++iX)
	{
		for(int t1=0; t1 < iRes/m_iW; ++t1)
		{
			for(int iY=0; iY<m_iH; ++iY)
			{
				for(int t2=0; t2 < iRes/m_iH; ++t2)
				{
					if(t1%4==0 && t2%4==0)
						ofstr << GetDoubleData(iX,iY) / 4. << " ";
					else
						ofstr << "0 ";
				}
			}
			ofstr << "\n";
		}
	}

	ofstr << "</detector_value>\n\n";
	ofstr << "</measurement_data>\n";

	ofstr << "\n</measurement_file>\n";
	ofstr.close();
	return true;
}

// PAD-Image zu TmpImg konvertieren
void TmpImage::ConvertPAD(PadImage* pPad)
{
	m_iW = pPad->GetPadConfig().GetImageWidth();
	m_iH = pPad->GetPadConfig().GetImageHeight();
	m_dMin = pPad->m_iMin;
	m_dMax = pPad->m_iMax;

	m_puiDaten = (unsigned int*)gc.malloc(sizeof(int)*m_iW*m_iH,
										"pad_image -> tmp_image");
	if(m_puiDaten==NULL)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Loader: Could not allocate memory (line "
			   << __LINE__ << ")!\n";
		return;
	}
	memcpy(m_puiDaten, pPad->m_puiDaten, m_iW*m_iH*sizeof(int));

	UpdateRange();
}

const Vec2d<int>& TmpImage::GetMaxCoord() const { return m_vecMax; }

bool TmpImage::FitGaussian(double &dAmp,
						   double &dCenterX, double &dCenterY,
						   double &dSpreadX, double &dSpreadY) const
{
	dAmp = GetDoubleMax();
	dCenterX = double(GetMaxCoord()[0]);
	dCenterY = double(GetMaxCoord()[1]);
	dSpreadX = 1.;
	dSpreadY = 1.;

	if(m_puiDaten)
		return ::FitGaussian(m_iW, m_iH, m_puiDaten,
							 dAmp, dCenterX, dCenterY, dSpreadX, dSpreadY);
	//else if(m_pdDaten)
	// ...

	return false;
}

// TODO: do a better version of this method!
TmpGraph TmpImage::GetRadialIntegration(double dAngleInc, double dRadInc,
										const Vec2d<double>& vecCenter,
										bool bAngMean) const
{
	const double dMaxRad = sqrt((double(GetWidth())/2.)*(double(GetWidth())/2.)
						   + (double(GetHeight())/2.)*(double(GetHeight())/2.));
	const int iSteps = int(dMaxRad / dRadInc);

	TmpGraph graph(&m_TofConfig);
	graph.m_iW = iSteps;
	graph.m_puiDaten = (unsigned int*)gc.malloc(sizeof(int)*iSteps,
										"tmp_image -> integration");
	memset(graph.m_puiDaten, 0, iSteps*sizeof(int));

	unsigned int uiTotalCnts = 0;

	for(int i=0; i<iSteps; ++i)
	{
		const double dBeginRad = double(i)*dRadInc;
		const double dEndRad = double(i+1)*dRadInc;

		Roi roi;
		roi.add(new RoiCircleRing(vecCenter,dBeginRad,dEndRad));

		// brute force search
		for(int iY=0; iY<GetHeight(); ++iY)
			for(int iX=0; iX<GetWidth(); ++iX)
			{
				bool bPixelInside = roi.IsInside(iX,iY) || roi.IsInside(iX,iY+1)
							|| roi.IsInside(iX+1,iY) || roi.IsInside(iX+1,iY+1);

				if(!bPixelInside)
					continue;

				double dFraction = roi.HowMuchInside(iX, iY);
				graph.m_puiDaten[i] += dFraction*double(GetIntData(iX, iY));
			}

		// bAngMean: graph is a radial slice with mean angular counts
		if(bAngMean)
		{
			graph.m_puiDaten[i] /= (dEndRad*dEndRad - dBeginRad*dBeginRad)*M_PI;
		}
		uiTotalCnts += graph.m_puiDaten[i];
	}

	if(!bAngMean)
	{
		logger.SetCurLogLevel(LOGLEVEL_INFO);
		logger << "Loader: Total counts summed = " << uiTotalCnts << "\n";
	}
	return graph;
}
