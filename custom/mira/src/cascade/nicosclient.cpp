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

#include <string.h>

#include "nicosclient.h"
#include "helper.h"
#include "logger.h"

#define IS_PAD	1
#define IS_TOF	0
#define IS_NONE	-1

NicosClient::NicosClient() : TcpClient(0, true), m_pad(0, true),
							 m_tof(0, true)
{
	GlobalConfig::Init();
}

NicosClient::~NicosClient()
{
	GlobalConfig::Deinit();
}

const QByteArray& NicosClient::communicate(const char* pcMsg)
{
	// to unlock mutex at the end of the scope
	// (alternative: __try...__finally or evil goto)
	cleanup<QMutex> _cleanup(m_mutex, &QMutex::unlock);

	m_mutex.lock();
	if(!sendmsg(pcMsg))
		return m_byEmpty;

	const QByteArray& arr = recvmsg();
	return arr;
}

unsigned int NicosClient::counts(const QByteArray& arr)
{
	if(arr.size()<4) return 0;

	int iPad = IsPad(arr.data());
	if(iPad == IS_NONE) return 0;
	bool bPad = (iPad == IS_PAD);

	if(!IsSizeCorrect(arr, bPad))
		return 0;

	if(bPad)
	{
		m_pad.SetExternalMem((unsigned int*)(arr.data()+4));
		return m_pad.GetCounts();
	}
	else
	{
		//-----------------------------------------------
		// REMOVE THIS AGAIN AFTER TEST
		std::cerr << "TOF debug test." << std::endl;
		return 0;
		//-----------------------------------------------

		m_tof.SetExternalMem((unsigned int*)(arr.data()+4));
		return m_tof.GetCounts();
	}
}

unsigned int NicosClient::counts(const QByteArray& arr, int iStartX, int iEndX,
								 int iStartY, int iEndY)
{
	if(arr.size()<4) return 0;

	int iPad = IsPad(arr.data());
	if(iPad == IS_NONE) return 0;
	bool bPad = (iPad == IS_PAD);

	if(!IsSizeCorrect(arr, bPad))
		return 0;

	if(bPad)
	{
		m_pad.SetExternalMem((unsigned int*)(arr.data()+4));
		return m_pad.GetCounts(iStartX, iEndX, iStartY, iEndY);
	}
	else
	{
		//-----------------------------------------------
		// REMOVE THIS AGAIN AFTER TEST
		std::cerr << "TOF debug test." << std::endl;
		return 0;
		//-----------------------------------------------

		m_tof.SetExternalMem((unsigned int*)(arr.data()+4));
		return m_tof.GetCounts(iStartX, iEndX, iStartY, iEndY);
	}
}

bool NicosClient::IsSizeCorrect(const QByteArray& arr, bool bPad)
{
	bool bOk = true;
	if(bPad)
	{
		if(m_pad.GetPadSize()*4 != arr.size()-4)
		{
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "NicosClient.counts: buffer size (" << arr.size()-4
				   << " bytes) != expected PAD size (" << m_pad.GetPadSize()*4
				   << " bytes)." << "\n";
			bOk = false;
		}
	}
	else
	{
		if(m_tof.GetTofSize()*4 != arr.size()-4)
		{
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "NicosClient.counts: buffer size (" << arr.size()-4
				   << " bytes) != expected TOF size (" << m_tof.GetTofSize()*4
				   << " bytes)." << "\n";
			bOk = false;
		}
	}
	return bOk;
}

int NicosClient::IsPad(const char* pcBuf)
{
	if(strncasecmp(pcBuf, "IMAG", 4) == 0)		// PAD
		return IS_PAD;
	else if(strncasecmp(pcBuf, "DATA", 4) == 0)	// TOF
		return IS_TOF;

	return IS_NONE;
}
