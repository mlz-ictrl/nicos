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

#ifndef __INSTR_CONF__
#define __INSTR_CONF__

#include <map>
#include <string>
#include <istream>
#include <stdio.h>
#include <sstream>
#include "../auxiliary/helper.h"

class CascConf
{
	public:
		typedef std::map<std::string, std::string> t_map;
		typedef t_map::iterator t_iter;
		typedef t_map::const_iterator t_constiter;


	protected:
		t_map m_map;

	public:
		CascConf();
		virtual ~CascConf();

		void Clear();

		bool Load(std::istream& istr);
		bool Load(const void* pv);
		bool Load(FILE* pf, unsigned int uiSize);
		bool Load(gzFile pf, unsigned int uiSize);
		bool Load(const char* pcCascFile, const char* pcConfEnding);

		std::string GetVal(const std::string& strKey, bool *pbHasKey=0) const;

		template<class T> void GetValAs(const std::string& strKey, T& tVal,
										bool *pbHasKey=0) const
		{
			bool bHasKey = false;
			std::string strVal = GetVal(strKey, &bHasKey);

			if(bHasKey)
			{
				std::istringstream istr(strVal);
				istr >> tVal;
			}

			if(pbHasKey) *pbHasKey = bHasKey;
		}

		friend std::ostream& operator<<(std::ostream& ostr, const CascConf& conf);

		const t_map& GetMap() const { return m_map; }
};

std::ostream& operator<<(std::ostream& ostr, const CascConf& conf);

#endif
