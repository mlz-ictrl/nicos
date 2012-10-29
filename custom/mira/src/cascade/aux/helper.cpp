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

#include "helper.h"
#include "../config/globals.h"

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <locale>
#include <string.h>
#include <math.h>
#include <limits>
#include <iomanip>

// file size
long GetFileSize(FILE* pf)
{
	long lPos = ftell(pf);

	fseek(pf, 0, SEEK_END);
	long lSize = ftell(pf);

	fseek(pf, lPos, SEEK_SET);
	return lSize;
}

long GetFileSize(const char* pcFileName)
{
	FILE* pf = fopen(pcFileName, "rb");
	if(!pf) return 0;

	long lSize = GetFileSize(pf);

	fclose(pf);
	return lSize;
}

std::string GetFileEnding(const char* pcFileName)
{
	int iLen = strlen(pcFileName);

	bool bFound = false;
	int iIdx;

	for(iIdx=iLen-1; iIdx>=0; --iIdx)
	{
		if(pcFileName[iIdx] == '.')
		{
			bFound = true;
			break;
		}
	}

	if(bFound)
		return std::string(pcFileName + iIdx+1);

	return std::string("");
}

//------------------------------------------------------------------------------

std::string trim(const std::string& str)
{
	char *pcStr = new char[str.length()+1];
	strcpy(pcStr, str.c_str());
	trim(pcStr);

	std::string strRet = pcStr;
	delete[] pcStr;
	return strRet;
}

void trim(char* pcStr)
{
	int iBegin = 0;
	int iLenStr = strlen(pcStr);

	// remove whitespaces from front of string
	for(int i=0; i<iLenStr; ++i)
	{
		if(pcStr[i]!=' ' && pcStr[i]!='\t')
		{
			iBegin = i;
			break;
		}
	}

	iLenStr -= iBegin;
	if(iBegin!=0)
		memmove(pcStr, pcStr+iBegin, iLenStr);

	// remove whitespaces from back of string
	for(int i=iLenStr-1; i>=0; --i)
	{
		if(pcStr[i]!=' ' && pcStr[i]!='\t')
		{
			pcStr[i+1] = 0;
			break;
		}
	}
}

std::string get_byte_str(unsigned int iSize)
{
	double dSize = 0.;
	std::string strUnit = " B";
	
	
	if(iSize > 1024*1024)
	{
		dSize = double(iSize)/(1024.*1024.);
		strUnit = " MB";
	}
	else if(iSize > 1024)
	{
		dSize = double(iSize)/1024.;
		strUnit = " kB";
	}

	std::ostringstream ostr;
	ostr << std::fixed << std::setprecision(2);
	
	ostr << dSize << strUnit;
	return ostr.str();
}

void find_and_replace(std::string& str1, const std::string& str_old,
						const std::string& str_new)
{
	std::size_t pos = str1.find(str_old);
	if(pos==std::string::npos)
		return;

	str1.replace(pos, str_old.length(), str_new);
}


std::pair<std::string, std::string>
split(const std::string& str, const std::string& splitter)
{
	std::string::const_iterator iter =
	std::search(str.begin(), str.end(),
				splitter.begin(), splitter.end());
	
	std::string strFirst, strLast;
	
	if(iter != str.end())
	{
		strFirst = str.substr(0, iter-str.begin());
		strLast = str.substr(iter-str.begin()+splitter.length(),
							 std::string::npos);
	}
	else
	{
		strFirst = str;
		strLast = "";
	}

	strFirst = trim(strFirst);
	strLast = trim(strLast);
	
	return std::pair<std::string, std::string>(strFirst, strLast);
}

//------------------------------------------------------------------------------


unsigned int endian_swap(unsigned int ui)
{
	return (ui>>24) | ((ui<<8)&0x00ff0000) | ((ui>>8)&0x0000ff00) | (ui<<24);
}


//------------------------------------------------------------------------------


class NumberGrouping : public std::numpunct<char>
{
	protected:
		virtual char do_thousands_sep() const
		{
			return ' ';
		}

		virtual std::string do_grouping() const
		{
			return "\03";
		}
};

void SetNumberGrouping(std::ostream& ostr)
{
	std::locale loc(ostr.getloc(), new NumberGrouping);
	ostr.imbue(loc);
}


//------------------------------------------------------------------------------

double safe_log10(double d)
{
	if(d>0.)
		d = log10(d);
	else
		// ungültige Werte weit außerhalb der Range verlagern
		d = /*-std::numeric_limits<double>::max()*/ -100.;

	return d;
}

double safe_log10_lowerrange(double d)
{
	if(d>0.)
		d = log10(d);
	else
		d = GlobalConfig::GetLogLowerRange();

	return d;
}

//------------------------------------------------------------------------------

static inline void init_rand()
{
	static bool s_bIsInited = false;
	if(s_bIsInited)
		return;
		
	srand(time(0));
	s_bIsInited = true;
}

double rand01()
{
	init_rand();
	return double(rand()) / double(RAND_MAX);
}

double randmp1()
{
	init_rand();
	return (double(rand())-double(RAND_MAX)*0.5) / double(RAND_MAX);
}
