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
// Im Speicher Daten per Zlib-Deflate dekomprimieren

#ifndef __DECOMPRESS__
#define __DECOMPRESS__

#include <zlib.h>
#include "logger.h"

// wrapper for zlib's uncompress function
bool zlib_decompress(const char* pcIn, int iLenIn, char* pcOut, int& iLenOut)
{
	uLong ulLenOut = iLenOut;
	int iErr = ::uncompress((Bytef*)pcOut, &ulLenOut,
							(Bytef*)pcIn, (uLong)iLenIn);
	iLenOut = ulLenOut;

	switch(iErr)
	{
		case Z_BUF_ERROR:
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "Zlib: out of memory." << "\n";
			break;
		case Z_MEM_ERROR:
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "Zlib: output buffer too small." << "\n";
			break;
		case Z_DATA_ERROR:
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "Zlib: invalid input data." << "\n";
			break;
	}
	return iErr==Z_OK;
}
#endif
