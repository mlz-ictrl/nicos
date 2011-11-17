// *****************************************************************************
// NICOS-NG, the Networked Instrument Control System of the FRM-II
// Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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

#include <stdio.h>
#include <locale>
#include <string.h>
#include "helper.h"

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
