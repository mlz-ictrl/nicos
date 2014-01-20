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

#include "conf.h"
#include "../auxiliary/helper.h"
#include <iostream>

CascConf::CascConf()
{}

CascConf::~CascConf()
{}

void CascConf::Clear()
{
	m_map.clear();
}

bool CascConf::Load(std::istream& istr)
{
	while(!istr.eof())
	{
		std::string strLine;

		std::getline(istr, strLine);
		std::pair<std::string, std::string> pairStr = split(strLine, ":");

		std::string strKey = pairStr.first;
		std::string strVal = pairStr.second;

		if(strKey != "")
		{
            if(strKey.length()>0 && strKey[0]=='#')
                continue;
			//std::cout << "key: \"" << strKey << "\", val: \"" << strVal << "\"" << std::endl;
			m_map[strKey] = strVal;
		}
	}

	return true;
}

bool CascConf::Load(const void* pv)
{
	const char* pc = (const char*)pv;

	std::istringstream istr(pc);
	return Load(istr);
}

bool CascConf::Load(FILE* pf, unsigned int uiSize)
{
	char *pc = new char[uiSize+1];
	pc[uiSize] = 0;
	unsigned int uiLen = fread(pc, 1, uiSize, pf);
	
	bool bOk = Load((void*)pc);
	delete[] pc;

	return bOk && (uiSize==uiLen);
}

bool CascConf::Load(gzFile pf, unsigned int uiSize)
{
	char *pc = new char[uiSize+1];
	pc[uiSize] = 0;
	unsigned int uiLen = gzread(pf, pc, uiSize);
	
	bool bOk = Load((void*)pc);
	delete[] pc;

	return bOk && (uiSize==uiLen);
}

bool CascConf::Load(const char* pcCascFile, const char* pcConfEnding)
{
	std::string strFile = std::string(pcCascFile) + std::string(pcConfEnding);

	std::ifstream ifstr(strFile.c_str());
	if(!ifstr.is_open())
		return false;
	
	return Load(ifstr);
}

std::string CascConf::GetVal(const std::string& strKey, bool *pbHasKey) const
{
	t_constiter iter = m_map.find(strKey);

	if(iter == m_map.end())
	{
		if(pbHasKey) *pbHasKey = false;
		return "";
	}

	if(pbHasKey) *pbHasKey = true;
	return (*iter).second;
}


std::ostream& operator<<(std::ostream& ostr, const CascConf& conf)
{
	for(CascConf::t_constiter iter=conf.m_map.begin();
		iter!=conf.m_map.end(); ++iter)
	{
		ostr << "key=\"" << (*iter).first << "\", value=\"" << (*iter).second << "\"\n";
	}

	return ostr;
}
