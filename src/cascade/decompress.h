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

// Im Speicher Daten per Zlib-Deflate dekomprimieren

#include <zlib.h>
#include <iostream>

bool decompress(const char* pcIn, int iLenIn, char* pcOut, int& iLenOut)
{
	z_stream zstr;
	memset(&zstr, 0, sizeof zstr);
	
	zstr.next_in = (Bytef*)pcIn;
	zstr.avail_in = (uInt)iLenIn;
	
	if(inflateInit(&zstr)!=Z_OK) 
	{
		std::cerr << "Konnte Zlib nicht initialisieren." << std::endl;
		return false;
	}
	
	zstr.next_out = (Bytef*)pcOut;
	zstr.avail_out = (uInt)iLenOut;
	
	if(inflate(&zstr, Z_FINISH)!=Z_STREAM_END)
	{
		std::cerr << "Dekompression fehlgeschlagen." << std::endl;
		return false;
	}
	
	iLenOut = (int)zstr.total_out;
	inflateEnd(&zstr);
	
	return true;
}
