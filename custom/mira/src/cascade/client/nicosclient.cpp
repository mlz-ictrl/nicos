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

#include <string.h>

#include "nicosclient.h"
#include "../auxiliary/helper.h"
#include "../auxiliary/logger.h"
//#include "../auxiliary/gc.h"

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
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "nicosclient: Could not send message to server.\n";
		return m_byEmpty;
	}

	const QByteArray& arr = recvmsg();

	if(arr.size()<4)
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "nicosclient: Server response too short.\n";
	}

	return arr;
}

bool NicosClient::communicate_and_save(const char* pcMsg, const char* pcDstFile,
										bool bSaveMsgPrefix)
{
	cleanup<QMutex> _cleanup(m_mutex, &QMutex::unlock);

	m_mutex.lock();
	if(!sendmsg(pcMsg))
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "nicosclient: Could not send message to server.\n";
		return false;
	}

	const QByteArray& arr = recvmsg();
	if(arr.size()<4)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "nicosclient: Server response too short.\n";
		return false;
	}

	FILE *pf = fopen(pcDstFile, "wb");
	if(!pf)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "nicosclient: Cannot open file \"" << pcDstFile << "\".\n";

		return false;
	}

	unsigned int uiSize = arr.size();
	const char* pData = arr.data();
	if(!bSaveMsgPrefix)
	{
		uiSize -= 4;
		pData += 4;
	}


	if(fwrite(pData, 1, uiSize, pf) != uiSize)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "nicosclient: Wrong number of bytes written to \""
				<< pcDstFile << "\".\n";
	}

	fflush(pf);
	fclose(pf);

	return true;
}

unsigned int NicosClient::counts(const QByteArray* parr)
{
	if(!parr) return 0;
	const QByteArray& arr = *parr;

	if(arr.size()<4) return 0;

	int iPad = IsPad(arr.data());
	if(iPad == IS_NONE) return 0;
	bool bPad = (iPad == IS_PAD);

	if(!IsSizeCorrect(&arr, bPad))
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "nicosclient: Wrong TOF/PAD size.\n";
		return 0;
	}

	if(bPad)
	{
		m_pad.SetExternalMem((unsigned int*)(arr.data()+4));
		return m_pad.GetCounts();
	}
	else
	{
		m_tof.SetExternalMem((unsigned int*)(arr.data()+4));
		return m_tof.GetCounts();
	}
}

unsigned int NicosClient::counts(const QByteArray* parr, int iStartX, int iEndX,
								 int iStartY, int iEndY)
{
	if(!parr) return 0;
	const QByteArray& arr = *parr;

	if(arr.size()<4) return 0;

	int iPad = IsPad(arr.data());
	if(iPad == IS_NONE) return 0;
	bool bPad = (iPad == IS_PAD);

	if(!IsSizeCorrect(&arr, bPad))
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "nicosclient: Wrong TOF/PAD size.\n";
		return 0;
	}

	if(bPad)
	{
		m_pad.SetExternalMem((unsigned int*)(arr.data()+4));
		return m_pad.GetCounts(iStartX, iEndX, iStartY, iEndY);
	}
	else
	{
		m_tof.SetExternalMem((unsigned int*)(arr.data()+4));
		return m_tof.GetCounts(iStartX, iEndX, iStartY, iEndY);
	}
}

bool NicosClient::contrast(const QByteArray* parr, int iFoil,
							double *pC, double *pPhase,
							double *pC_err, double *pPhase_err)
{
	if(!parr) return 0;
	const QByteArray& arr = *parr;

	if(arr.size()<4) return 0;

	int iPad = IsPad(arr.data());
	if(iPad == IS_NONE) return 0;
	bool bTof = (iPad == IS_TOF);

	if(!IsSizeCorrect(&arr, !bTof))
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "nicosclient: Wrong TOF/PAD size.\n";		
		return false;
	}

	bool bOk = true;

	if(bTof)
	{
		m_tof.SetExternalMem((unsigned int*)(arr.data()+4));

		TmpGraph graph;
		if(iFoil<0)
			graph = m_tof.GetTotalGraph();
		else
			graph = m_tof.GetGraph(iFoil);

		if(pC_err && pPhase_err)
			bOk = graph.GetContrast(*pC, *pPhase, *pC_err, *pPhase_err);
		else
			bOk = graph.GetContrast(*pC, *pPhase);
	}
	else
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "nicosclient: Cannot calculate MIEZE contrast/phase for PAD image.\n";
		return false;
	}

	//gc.print();
	return bOk;
}

bool NicosClient::contrast(const QByteArray* parr, int iFoil,
							int iStartX, int iEndX,
							int iStartY, int iEndY,
							double *pC, double *pPhase,
							double *pC_err, double *pPhase_err)
{
	if(!parr) return 0;
	const QByteArray& arr = *parr;

	if(arr.size()<4) return 0;

	int iPad = IsPad(arr.data());
	if(iPad == IS_NONE) return 0;
	bool bTof = (iPad == IS_TOF);

	if(!IsSizeCorrect(&arr, !bTof))
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "nicosclient: Wrong TOF/PAD size.\n";
		return false;
	}

	bool bOk = true;

	if(bTof)
	{
		m_tof.SetExternalMem((unsigned int*)(arr.data()+4));

		TmpGraph graph;
		if(iFoil<0)
			graph = m_tof.GetTotalGraph(iStartX, iEndX, iStartY, iEndY);
		else
			graph = m_tof.GetGraph(iStartX, iEndX, iStartY, iEndY, iFoil);

		if(pC_err && pPhase_err)
			bOk = graph.GetContrast(*pC, *pPhase, *pC_err, *pPhase_err);
		else
			bOk = graph.GetContrast(*pC, *pPhase);
	}
	else
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "nicosclient: Cannot calculate MIEZE contrast/phase for PAD image.\n";
		return false;
	}

	//gc.print();
	return bOk;
}

bool NicosClient::IsSizeCorrect(const QByteArray* parr, bool bPad)
{
	if(!parr) return 0;
	const QByteArray& arr = *parr;

	bool bOk = true;
	if(bPad)
	{
		if(m_pad.GetPadSize()*4 != arr.size()-4)
		{
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "nicosclient: buffer size (" << arr.size()-4
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
			logger << "nicosclient: buffer size (" << arr.size()-4
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
