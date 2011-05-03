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
//#include "tofloader.h"


NicosClient::NicosClient() : TcpClient(0, true)
{
	//Config_TofLoader::Init();
}

NicosClient::~NicosClient()
{
	//Config_TofLoader::Deinit();
}

const QByteArray& NicosClient::communicate(const char* pcMsg)
{
	m_mutex.lock();
	
	bool success = sendmsg(pcMsg);
	if(!success)
	{
		m_mutex.unlock();
		return m_byEmpty;
	}
	const QByteArray& arr = recvmsg();
	
	m_mutex.unlock();
	return arr;
}
