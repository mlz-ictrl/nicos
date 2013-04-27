// *****************************************************************************
// NICOS, the Networked Instrument Control System of the FRM-II
// Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

#ifndef __CASCADE_CONFIG__
#define __CASCADE_CONFIG__

#include <string>

#include "../auxiliary/xml.h"

/**
 * \brief (Singleton) class for reading xml files
 */
class Config : public Xml
{
	private:
		static Config *s_pConfig;

	public:
		Config();
		virtual ~Config();

		/// get pointer to singleton instance of this class
		static Config* GetSingleton();
		static void ClearSingleton();
};

#endif
