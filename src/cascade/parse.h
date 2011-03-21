// *****************************************************************************
// Module:
//   $Id$
//
// Author:
//   Tobias Weber <tweber@frm2.tum.de>
//
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
// *****************************************************************************

// einfache Argumentstrings der Sorte "status=1 error=0" lesen und eine Hashmap daraus machen

#ifndef __PRIMITIV_PARSER__
#define __PRIMITIV_PARSER__

#include <stdlib.h>
#include <string>
#include <map>
#include <sstream>

class ArgumentMap
{
	protected:
		std::map<std::string, std::string> m_mapArgs;
		
	public:
		//////////////// Neue Wertepaare (z.B. "status=1 error=0") hinzufügen ///////////
		void add(const char* pcStr)
		{
			std::istringstream istr(pcStr);
			
			while(!istr.eof())
			{
				std::string str;
				istr >> str;
		
				int iPos = str.find("=");
				if(iPos == std::string::npos)
				{
					std::cerr << "Fehler beim Parsen des Strings: \"" << pcStr << "\"" << std::endl;
					break;
				}
				
				// links des Gleichheitszeichens
				std::string strLinks = str.substr(0,iPos);
				
				// rechts des Gleichheitszeichens
				std::string strRechts = str.substr(iPos+1, str.length()-iPos-1);;
				m_mapArgs.insert(std::pair<std::string,std::string>(strLinks, strRechts));
				
				//std::cout << "Links: \"" << strLinks << "\", Rechts: \"" << strRechts << "\"" << std::endl;
			}
		}
		/////////////////////////////////////////////////////////////////////////////////
		
		/////////////////////////////// Werte abfragen /////////////////////////////
		const char* QueryString(const char* pcKey) const
		{
			std::map<std::string,std::string>::const_iterator iter = m_mapArgs.find(pcKey);
			if(iter == m_mapArgs.end())
				return 0;
			return iter->second.c_str();
		}
		
		int QueryInt(const char* pcKey, int iDefault=0) const
		{
			const char* pcStr = QueryString(pcKey);
			if(pcStr==NULL) return iDefault;
			
			return atoi(pcStr);
		}
		////////////////////////////////////////////////////////////////////////////
		
		
		ArgumentMap(const char* pcStr)
		{
			add(pcStr);
		}
	
		virtual ~ArgumentMap()
		{}
};

#endif
