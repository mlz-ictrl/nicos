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

#include <iostream>

#include "nicosclient.h"
#include "helper.h"
#include "tofloader.h"


NicosClient::NicosClient() : TcpClient(0, true)
{
	Config_TofLoader::Init();
}

NicosClient::~NicosClient()
{
	Config_TofLoader::Deinit();
}

const QByteArray& NicosClient::communicate(const char* pcMsg)
{
	cleanup<QMutex> _cleanup(m_mutex, &QMutex::unlock);	// unlock mutex at the end of the scope
	
	m_mutex.lock();
	if(!sendmsg(pcMsg))
		return m_byEmpty;
	
	const QByteArray& arr = recvmsg();
	return arr;
}

unsigned int NicosClient::counts(const QByteArray& arr, bool bPad)
{
	if(bPad)
	{
		const PadImage* pPad = (const PadImage*)arr.data();
		return pPad->GetCounts();
	}
	else
	{
		const TofImage* pTof = (const TofImage*)arr.data();
		return pTof->GetCounts();
	}
}

unsigned int NicosClient::counts(const QByteArray& arr, bool bPad, int iStartX, int iEndX, int iStartY, int iEndY)
{
	if(bPad)
	{
		const PadImage* pPad = (const PadImage*)arr.data();
		return pPad->GetCounts(iStartX, iEndX, iStartY, iEndY);
	}
	else
	{
		const TofImage* pTof = (const TofImage*)arr.data();
		return pTof->GetCounts(iStartX, iEndX, iStartY, iEndY);
	}
}
