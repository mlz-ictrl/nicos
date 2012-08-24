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

#include "parse.h"

#include <iostream>
#include "helper.h"
#include "logger.h"

#ifdef USE_BOOST
	#include <boost/xpressive/xpressive.hpp>
	#include <boost/xpressive/regex_actions.hpp>
	using namespace boost::xpressive;
#else
	#include <sstream>
#endif


ArgumentMap::ArgumentMap(const char* pcStr)
{
	if(pcStr)
		add(pcStr);
}

ArgumentMap::~ArgumentMap()
{}

// parse pcStr and add all "key=value" pairs to map
void ArgumentMap::add(const char* pcStr)
{
	std::string str = trim(std::string(pcStr));

#ifdef USE_BOOST // use cooler boost version or plain old manual version?

	// diese sregex-Ausdrücke basieren auf dem Beispiel zu
	// "Semantic Actions and User-Defined Assertions"
	// aus der xpressive-Dokumentation:
	// http://www.boost.org/doc/libs/1_46_1/doc/html/xpressive/user_s_guide.html
	sregex keyvalue = ((s1 = +_w) >>
					   *_s >> "=" >> *_s >>
					   (s2 = +_w))
					  [ref(m_mapArgs)[s1] = as<std::string>(s2)];
	regex_match(str, sregex(keyvalue >> *(+_s >> keyvalue)));

#else

	std::istringstream istr(str);

	while(!istr.eof())
	{
		std::string str;
		istr >> str;

		size_t iPos = str.find("=");
		if(iPos == std::string::npos)
		{
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "Argument Parser: Error parsing string: \"" << str
				   << "\"\n";
			break;
		}

		// links des Gleichheitszeichens
		std::string strLinks = str.substr(0,iPos);

		// rechts des Gleichheitszeichens
		std::string strRechts = str.substr(iPos+1, str.length()-iPos-1);
		m_mapArgs.insert(std::pair<std::string,std::string>
										(strLinks, strRechts));

		//std::cout << "Links: \"" << strLinks
		//			<< "\", Rechts: \"" << strRechts << "\""
		//			<< std::endl;
	}

#endif //USE_BOOST
}
//----------------------------------------------------------------------

//----------------------------------------------------------------------
// get cstring value corresponding to key pcKey
// if pcKey isn't found, return NULL
const char* ArgumentMap::QueryString(const char* pcKey) const
{
	std::map<std::string,std::string>::const_iterator iter =
												  m_mapArgs.find(pcKey);
	if(iter == m_mapArgs.end())
		return 0;
	return iter->second.c_str();
}

// get string value corresponding to key pcKey
// if pcKey isn't found, use strDefault
// return a pair with a bool indicating if the key was found and the value
std::pair<bool, std::string> ArgumentMap::QueryString(const char* pcKey,
				 const std::string& strDefault) const
{
	std::pair<bool, std::string> pairRet;

	std::map<std::string,std::string>::const_iterator iter =
												  m_mapArgs.find(pcKey);

	if(iter == m_mapArgs.end())
	{
		pairRet.first = false;
		pairRet.second = strDefault;
		return pairRet;
	}
	pairRet.first = true;
	pairRet.second = (*iter).second;

	return pairRet;
}

// get int value corresponding to key pcKey
// if pcKey isn't found, use iDefault
// return a pair with a bool indicating if the key was found and the value
std::pair<bool, int> ArgumentMap::QueryInt(const char* pcKey, int iDefault) const
{
	std::pair<bool, int> pairRet;

	const char* pcStr = QueryString(pcKey);
	if(pcStr==NULL)
	{
		pairRet.first = false;
		pairRet.second = iDefault;
		return pairRet;
	}

	pairRet.first = true;
	pairRet.second = atoi(pcStr);

	return pairRet;
}

// get double value corresponding to key pcKey
// if pcKey isn't found, use dDefault
// return a pair with a bool indicating if the key was found and the value
std::pair<bool, double> ArgumentMap::QueryDouble(const char* pcKey, double dDefault) const
{
	std::pair<bool, double> pairRet;

	const char* pcStr = QueryString(pcKey);
	if(pcStr==NULL)
	{
		pairRet.first = false;
		pairRet.second = dDefault;
		return pairRet;
	}

	pairRet.first = true;
	pairRet.second = atof(pcStr);

	return pairRet;
}


//----------------------------------------------------------------------

// dump map contents for debugging
void ArgumentMap::dump() const
{
	std::map<std::string,std::string>::const_iterator iter;
	for(iter = m_mapArgs.begin(); iter!=m_mapArgs.end(); ++iter)
	{
		std::cout << "Key: \'" << (*iter).first << "\', "
				  << "Value: \'" << (*iter).second << "\'\n";
	}
}
