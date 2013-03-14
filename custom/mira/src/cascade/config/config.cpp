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
// (singleton) class for reading xml files

#include "config.h"

#include <iostream>
#include <stdlib.h>
#include <string.h>

#include "../auxiliary/logger.h"
#include "../auxiliary/helper.h"

Config::Config() {}
Config::~Config() {}

//////////////////////////////// Singleton-Zeug ////////////////////////////////
Config *Config::s_pConfig = 0;

Config* Config::GetSingleton()
{
	if(!s_pConfig) s_pConfig = new Config();
	return s_pConfig;
}

void Config::ClearSingleton()
{
	if(s_pConfig)
	{
		delete s_pConfig;
		s_pConfig = 0;
	}
}
////////////////////////////////////////////////////////////////////////////////

/*int main(void)
{
	Config::GetSingleton()->Load("./cascade.xml");
	std::cout << Config::GetSingleton()->QueryInt(
	 					"/cascade_config/tof_loader/image_width") << std::endl;
	std::cout << Config::GetSingleton()->QueryInt(
	 					"/cascade_config/tof_loader/image_height") << std::endl;
	Config::ClearSingleton();
	return 0;
}*/
