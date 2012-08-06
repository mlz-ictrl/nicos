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
// blockierend und nichtblockierend nutzbarer TCP-Client
// "Protokoll": 4 Bytes (int) = Größe der Nachricht; Nachricht

#include "client.h"
#include <stdlib.h>
#include "config.h"
#include "helper.h"
#include "logger.h"

#define WAIT_DELAY 5000

TcpClient::TcpClient(QObject *pParent, bool bBlocking)
								: QObject(pParent),
								  m_bBlocking(bBlocking),
								  m_socket(pParent),
								  m_bBeginOfMessage(1),
								  m_iCurMsgLength(0)
{
	m_iMessageTimeout = -1;	// "-1" bedeutet: Timeout nicht benutzen

// Cascade-Qt-Client?
#ifdef __CASCADE_QT_CLIENT__
	bool bUseMessageTimeout = (bool)Config::GetSingleton()
					->QueryInt("/cascade_config/server/use_message_timeout", 0);
	if(bUseMessageTimeout)
		m_iMessageTimeout = Config::GetSingleton()
					->QueryInt("/cascade_config/server/message_timeout", 10000);
#else	// Nicos-Client
	m_iMessageTimeout = 5000;
#endif

	connect(&m_socket, SIGNAL(connected()), this, SLOT(connected()));
	connect(&m_socket, SIGNAL(disconnected()), this, SLOT(disconnected()));
	if(!m_bBlocking)
		connect(&m_socket, SIGNAL(readyRead()), this, SLOT(readReady()));

	logger.SetCurLogLevel(LOGLEVEL_INFO);
	logger << "Client: Set to "
		   << (m_bBlocking? "blocking" : "non-blocking")
		   << " mode." << "\n";

}

TcpClient::~TcpClient()
{
	disconnect();
}

/////////////////////// Verbindung /////////////////////////////
bool TcpClient::connecttohost(const char* pcAddr, int iPort)
{
	disconnect();

	// Namen auflösen
	QHostInfo info = QHostInfo::fromName(pcAddr);
	if(info.addresses().isEmpty())
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Client: " << pcAddr << " could not be resolved.\n";
		return false;
	}
	m_addr = info.addresses().first();
	m_iPort = iPort;

	// Verbinden
	m_socket.connectToHost(m_addr, quint16(m_iPort));
	bool bConnected = m_socket.waitForConnected(WAIT_DELAY);
	return bConnected;
}

bool TcpClient::reconnect()
{
	disconnect();

	m_socket.connectToHost(m_addr, quint16(m_iPort));
	bool bConnected = m_socket.waitForConnected(WAIT_DELAY);

	if(!bConnected)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Client: Connection could not be reestablished.\n";
	}
	return bConnected;
}

void TcpClient::disconnect()
{
	if(m_socket.state()!=QAbstractSocket::UnconnectedState)
		m_socket.abort();
}

bool TcpClient::isconnected() const
{
	return (m_socket.state()==QAbstractSocket::ConnectedState);
}
////////////////////////////////////////////////////////////////


/////////////////////////// schreiben //////////////////////////
// Nachrichten mit Längen-Int vorne senden
bool TcpClient::sendmsg(const char *pcMsg)
{
	if(!isconnected())
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Client: Client not connected, could not send message.\n";
		return false;
	}

	int iLen = strlen(pcMsg);

	// Länge der folgenden Nachricht übertragen
	if(!write((char*)&iLen, 4, true))
		return false;

	// Nachricht übertragen
	return write(pcMsg, iLen, false);
}

bool TcpClient::write(const char* pcBuf, int iSize, bool bIsBinary)
{
	if(m_socket.write(pcBuf, iSize)==-1)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Client: Error writing to socket.\n";
		return false;
	}
	//m_socket.flush();

	if(!bIsBinary)
	{
		logger.green(false);
		logger.SetCurLogLevel(LOGLEVEL_INFO);
		logger << "[to server] length: " << iSize << ", data: "
			   << pcBuf << "\n";
		logger.normal();
	}
	return true;
}

bool TcpClient::sendfile(const char* pcFileName)
{
	logger.SetCurLogLevel(LOGLEVEL_INFO);
	logger << "Client: Sending \"" << pcFileName << "\"\n";

	FILE *pf = fopen(pcFileName,"rb");
	if(!pf)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Client: Could not open file \"" << pcFileName
			   << "\" for reading.\n";
		return false;
	}

	long iSize = GetFileSize(pf);

	char *pcDaten = new char[iSize];
	if(!fread(pcDaten, 1, iSize, pf))
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Client: Could not read file \"" << pcFileName << "\".\n";
		fclose(pf);
		delete[] pcDaten;
		return false;
	}
	fclose(pf);
	if(!write((char*)pcDaten,iSize))
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Client: Could not send file \"" << pcFileName << "\".\n";
	}
	delete[] pcDaten;

	logger.SetCurLogLevel(LOGLEVEL_INFO);
	logger << "Client: " << iSize << " bytes sent.\n";
	return true;
}
////////////////////////////////////////////////////////////////


///////////////////////// lesen ////////////////////////////////
int TcpClient::read(char* pcData, int iLen)
{
	int iLenRead = m_socket.read(pcData, iLen);
	if(iLenRead<0)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Client: Could not read socket.\n";
		iLenRead = 0;
	}
	return iLenRead;
}

const QByteArray& TcpClient::recvmsg(void)
{
	// nur für blockierenden Client erlauben
	if(!m_bBlocking)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Client: recvmsg not allowed in nonblocking mode.\n";
		return m_byEmpty;
	}

	m_timer.start();
	if(!m_socket.waitForReadyRead(WAIT_DELAY))
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Client: Socket timed out while receiving.\n";
		return m_byEmpty;
	}

	int iExpectedMsgLength=0;
	read((char*)&iExpectedMsgLength, 4);

	if(iExpectedMsgLength <= 0)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Client: Invalid message length: " << iExpectedMsgLength
			   << "\n";
		return m_byEmpty;
	}

	QByteArray& arrMsg = m_byCurMsg;
	arrMsg.resize(iExpectedMsgLength);

	while(m_socket.bytesAvailable() < iExpectedMsgLength)
	{
		if(!m_socket.waitForReadyRead(WAIT_DELAY))
		{
			logger.SetCurLogLevel(LOGLEVEL_ERR);
			logger << "Client: Socket timed out while receiving.\n";
			return m_byEmpty;
		}
	}

	int iRead = read(arrMsg.data(), iExpectedMsgLength);
	if(iRead!=iExpectedMsgLength)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Client: Wrong number of bytes received.\n";
		return m_byEmpty;
	}

	int iTimeElapsed = m_timer.elapsed();

	logger.green(true);
	logger.SetCurLogLevel(LOGLEVEL_INFO);
	logger << "[from server] length: " << iExpectedMsgLength
		   << ", time: " << iTimeElapsed << "ms, data: " << arrMsg.data()
		   << "\n";
	logger.normal();

	return arrMsg;
}
////////////////////////////////////////////////////////////////


///////////////////////////// Slots ////////////////////////////
void TcpClient::connected()
{
	logger.SetCurLogLevel(LOGLEVEL_INFO);
	logger << "Client: Connected to server "
		   << m_addr.toString().toAscii().data()
		   << " at port " << m_iPort << ".\n";
}

void TcpClient::disconnected()
{
	logger.SetCurLogLevel(LOGLEVEL_INFO);
	logger << "Client: Disconnected from server "
		   << m_addr.toString().toAscii().data()
		   << " at port " << m_iPort << ".\n";
}

void TcpClient::readReady()
{
	// nur für nichtblockierenden Client erlauben
	if(m_bBlocking)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Client: readReady not allowed in blocking mode.\n";
		return;
	}

	int iSize = m_socket.bytesAvailable();
	if(iSize==0) return;

	// Falls Timeout-Wert gesetzt
	if(m_iMessageTimeout>=0)
	{
		// falls Nachricht zu lange braucht, resetten
		if(!m_bBeginOfMessage && m_timer.elapsed()>m_iMessageTimeout)
		{
			m_bBeginOfMessage = true;
			m_iExpectedMsgLength = m_iCurMsgLength = 0;

			logger.SetCurLogLevel(LOGLEVEL_WARN);
			logger << "Client: Message timeout reached.\n";
		}
	}

	// Am Anfang einer Nachricht kommt ein Int, der deren Größe angibt
	if(m_bBeginOfMessage)
	{
		if(iSize < 4) return;
		iSize -= 4;

		// Länge der zu erwartenden Nachricht lesen
		m_iExpectedMsgLength = m_iCurMsgLength = 0;
		if(read((char*)&m_iExpectedMsgLength, 4)==0)
			return;

		if(m_iExpectedMsgLength==0)
		{
			logger.SetCurLogLevel(LOGLEVEL_WARN);
			logger << "Client: Server sent message length 0. "
				   << "Trying to reset connection.\n";

			reconnect();
			return;
		}

		// Nachricht läuft
		m_bBeginOfMessage = false;
		m_timer.start();

		m_byCurMsg.resize(m_iExpectedMsgLength);
	}

	int iMsgLeft = m_iExpectedMsgLength - m_iCurMsgLength;
	if(iSize>iMsgLeft) iSize = iMsgLeft;

	char* pcBuf = m_byCurMsg.data() + m_iCurMsgLength;
	int iLenRead = read(pcBuf, iSize);
	m_iCurMsgLength += iLenRead;

	// Ende der gegenwärtigen Nachricht erreicht?
	if(m_iCurMsgLength>=m_iExpectedMsgLength)
	{
		if(m_iCurMsgLength > m_iExpectedMsgLength)
		{
			logger.SetCurLogLevel(LOGLEVEL_WARN);
			logger << "Client: Got too much data; expected: "
				   << m_iExpectedMsgLength
				   << ", received: " << m_iCurMsgLength
				   << "\n";
		}

		int iTimeElapsed = m_timer.elapsed();

		// nur senden, falls nicht leer
		if(m_iCurMsgLength > 0)
		{
			emit MessageSignal(m_byCurMsg.data(), m_byCurMsg.size());

			logger.green(true);
			logger.SetCurLogLevel(LOGLEVEL_INFO);
			logger << "[from server] length: " << m_iCurMsgLength
				   << ", time: " << iTimeElapsed << "ms, total: "
				   << m_timer.elapsed() << "ms, data: "
				   << m_byCurMsg.data()
				   << "\n";
			logger.normal();

			// Ende der Nachricht, neue beginnt
			m_bBeginOfMessage = true;
			m_iExpectedMsgLength = m_iCurMsgLength = 0;
		}
	}
}
////////////////////////////////////////////////////////////////

void TcpClient::SetTimeout(int iTimeout) { m_iMessageTimeout = iTimeout; }
