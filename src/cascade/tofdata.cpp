// Klassen, um die TOF- und PAD-Datentypen mit Qwt zu nutzen

#include <limits>
#include <math.h>
#include <iostream>
#include "tofdata.h"

MainRasterData::MainRasterData(const QwtDoubleRect& rect) : QwtRasterData(rect), m_bLog(1)
{
}

void MainRasterData::SetLog10(bool bLog10)
{ 
	m_bLog = bLog10;
}

bool MainRasterData::GetLog10(void) const
{ 
	return m_bLog;
}



// *********************** PAD-Daten *********************** 
PadData::PadData() : MainRasterData(QwtDoubleRect(0,Config_TofLoader::BILDBREITE,0,Config_TofLoader::BILDHOEHE))
{
}

PadData::PadData(const PadData& pad) : MainRasterData(QwtDoubleRect(0,Config_TofLoader::BILDBREITE,0,Config_TofLoader::BILDHOEHE)), PadImage(pad)
{
	m_bLog = pad.m_bLog;
}

PadData::~PadData()
{
}

QwtRasterData *PadData::copy() const
{
	//std::cout << "copy" << std::endl;
	return new PadData(*this);
}

QwtDoubleInterval PadData::range() const
{
	if(m_puiDaten==NULL) return QwtDoubleInterval(0.,1.);
	
	if(m_bLog)
	{
		double dTmpMax = m_iMax,
			dTmpMin = m_iMin;
		
		if(dTmpMax>0.) dTmpMax = log10(dTmpMax); else dTmpMax=Config_TofLoader::LOG_LOWER_RANGE;
		if(dTmpMin>0.) dTmpMin = log10(dTmpMin); else dTmpMin=Config_TofLoader::LOG_LOWER_RANGE;
		
		if(dTmpMax!=dTmpMax) dTmpMax=0.;
		if(dTmpMin!=dTmpMin) dTmpMin=0.;
		
		return QwtDoubleInterval(dTmpMin,dTmpMax);
	}
	else
	{
		return QwtDoubleInterval(m_iMin,m_iMax);
	}
}
    

double PadData::value(double x, double y) const
{
	double dRet=(double)GetData((int)x,(int)y);
	
	if(m_bLog)
	{
		if(dRet>0.)
			dRet = log10(dRet);
		else
			dRet = -std::numeric_limits<double>::max(); // ungültige Werte weit außerhalb der Range verlagern
	}
	
	if(dRet!=dRet) dRet=0.;
	return dRet;
}

double PadData::GetValueRaw(int x, int y) const
{
	return (double)GetData(x,y);
}

// ***********************************************************


// *********************** TOF-Daten *********************** 
Data2D::Data2D(const QwtDoubleRect& rect) : MainRasterData(rect), m_bPhaseData(0)
{
}

Data2D::Data2D() : MainRasterData(QwtDoubleRect(0,Config_TofLoader::BILDBREITE,0,Config_TofLoader::BILDHOEHE))
{
}

Data2D::Data2D(const Data2D& data2d) : MainRasterData(QwtDoubleRect(0,data2d.m_iW,0,data2d.m_iH)), TmpImage(data2d)
{
	this->m_bLog = data2d.m_bLog;
	this->m_bPhaseData = data2d.m_bPhaseData;
}

Data2D::~Data2D()
{
	clearData();
}
		
void Data2D::SetPhaseData(bool bPhaseData)	// wegen Achsen-Range
{
	m_bPhaseData = bPhaseData;
}

void Data2D::clearData()
{
	if(m_puiDaten!=NULL) { delete[] m_puiDaten; m_puiDaten = NULL; }
	if(m_pdDaten!=NULL) { delete[] m_pdDaten; m_pdDaten = NULL; }
}

QwtRasterData *Data2D::copy() const
{
	return new Data2D(*this);
}
	
QwtDoubleInterval Data2D::range() const
{
	if(m_puiDaten==NULL && m_pdDaten==NULL) return QwtDoubleInterval(0.,1.);
	
	double dTmpMax, dTmpMin;
	if(m_bPhaseData)
	{
		dTmpMax=360.;
		dTmpMin=0.;
	}
	else
	{
		dTmpMax = m_dMax;
		dTmpMin = m_dMin;
	}
	
	if(m_bLog)
	{
		if(dTmpMax>0.) dTmpMax = log10(dTmpMax); else dTmpMax=Config_TofLoader::LOG_LOWER_RANGE;
		if(dTmpMin>0.) dTmpMin = log10(dTmpMin); else dTmpMin=Config_TofLoader::LOG_LOWER_RANGE;
		
		if(dTmpMax!=dTmpMax) dTmpMax=0.;
		if(dTmpMin!=dTmpMin) dTmpMin=0.;
		
		return QwtDoubleInterval(dTmpMin,dTmpMax);
	}
	else
		return QwtDoubleInterval(dTmpMin,dTmpMax);
}

double Data2D::value(double x, double y) const
{
	double dRet=(double)GetData((int)x,(int)y);
	
	if(m_bLog)
	{
		if(dRet>0.)
			dRet = log10(dRet);
		else
			dRet = -std::numeric_limits<double>::max(); // ungültige Werte weit außerhalb der Range verlagern
	}
	
	if(dRet!=dRet) dRet=0.;
	return dRet;
}

double Data2D::GetValueRaw(int x, int y) const
{
	return (double)GetData(x,y);
}

// **********************************************************
