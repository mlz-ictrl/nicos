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

#ifndef __ARGUMENT_MAP_PARSER__
#define __ARGUMENT_MAP_PARSER__

#include <stdlib.h>
#include <string>
#include <map>

/*
 * ArgumentMap
 * parse simple strings of the type "status=1 error=0" and sort them into a map
 */
class ArgumentMap
{
	protected:
		std::map<std::string, std::string> m_mapArgs;

	public:
		ArgumentMap(const char* pcStr=0);

		virtual ~ArgumentMap();

		// parse pcStr and add all "key=value" pairs to map
		void add(const char* pcStr);

		// get cstring value corresponding to key pcKey
		// if pcKey isn't found, return NULL
		const char* QueryString(const char* pcKey) const;

		// get string value corresponding to key pcKey
		// if pcKey isn't found, use strDefault
		// return a pair with a bool indicating if the key was found and the value
		std::pair<bool, std::string> QueryString(const char* pcKey,
						 const std::string& strDefault) const;


		// get int value corresponding to key pcKey
		// if pcKey isn't found, use iDefault
		// return a pair with a bool indicating if the key was found and the value
		std::pair<bool, int> QueryInt(const char* pcKey, int iDefault=0) const;

		// get double value corresponding to key pcKey
		// if pcKey isn't found, use dDefault
		// return a pair with a bool indicating if the key was found and the value
		std::pair<bool, double>  QueryDouble(const char* pcKey, double dDefault=0.) const;

		// dump map contents for debugging
		void dump() const;
};
#endif
