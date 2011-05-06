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
// blockierend und nichtblockierend nutzbarer TCP-Client
// "Protokoll": 4 Bytes (int) = Größe der Nachricht; Nachricht

#include "client.h"
#include <iostream>
#include <stdlib.h>
#include "config.h"
#include "helper.h"

#define WAIT_DELAY 5000

/////////////////////// Verbindung /////////////////////////////
bool TcpClient::connecttohost(const char* pcAddr, int iPort)
{
	disconnect();
	
	// Namen auflösen
	QHostInfo info = QHostInfo::fromName(pcAddr);
	if(info.addresses().isEmpty())
	{
		std::cerr << "Error: " << pcAddr << " could not be resolved." << std::endl;
		return false;
	}
	QHostAddress address = info.addresses().first();
	/*QHostAddress address = QHostAddress(QString(pcAddr))*/ 
	
	// Verbinden
	m_socket.connectToHost(address, quint16(iPort));
	bool bConnected = m_socket.waitForConnected(WAIT_DELAY);

//	if(!bConnected)
//		std::cerr << "Error: Could not connect to " << pcAddr << " on port " << iPort << "." << std::endl;

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
		return false;

	// Fehler im Server: Sollte eigentlich nicht 0-terminiert werden müssen
	int iLen = strlen(pcMsg)+1;
	
	// Länge der folgenden Nachricht übertragen
	if(!write((char*)&iLen, 4)) 
		return false;
	
	// Nachricht übertragen
	return write(pcMsg, iLen);
	
	/*
	char pcBuf[256];
	strcpy(pcBuf+4, pcMsg);
	*((int*)pcBuf) = iLen;
	write(pcBuf, iLen+4);
	*/
}

bool TcpClient::write(const char* pcBuf, int iSize)
{
	if(m_socket.write(pcBuf, iSize)==-1)
		return false;
	//m_socket.flush();
	
	if(m_bDebugLog && iSize>0 && isprint(pcBuf[0]))
		std::cerr << "\033[0;31m" << "[to server] length: " << iSize << ", data: " << pcBuf << "\033[0m" << std::endl;

	return true;
}

bool TcpClient::sendfile(const char* pcFileName)
{
	std::cerr << "Sende \"" << pcFileName << "\"" << std::endl;
	FILE *pf = fopen(pcFileName,"rb");
	if(!pf)
	{ 
		std::cerr << "Error: Could not open file \"" << pcFileName << "\"." << std::endl;
		return false;
	}
	
	long iSize = GetFileSize(pf);
	
	char *pcDaten = new char[iSize];
	if(!fread(pcDaten, 1, iSize, pf))
	{
		std::cerr << "Error: Could not read file \"" << pcFileName << "\"." << std::endl;
		fclose(pf);
		delete[] pcDaten;
		return false;
	}
	fclose(pf);
	if(!write((char*)pcDaten,iSize))
		std::cerr << "Error: Could not send file \"" << pcFileName << "\"." << std::endl;
	delete[] pcDaten;
	
	std::cerr << iSize << " bytes sent." << std::endl;
	return true;
}
////////////////////////////////////////////////////////////////


///////////////////////// lesen ////////////////////////////////
int TcpClient::read(char* pcData, int iLen)
{
	int iLenRead = m_socket.read(pcData, iLen);
	if(iLenRead<0)
	{
		std::cerr << "Error: Could not read socket." << std::endl;
		iLenRead = 0;
	}
	return iLenRead;
}

const QByteArray& TcpClient::recvmsg(void)
{
	// nur für blockierenden Client erlauben
	if(!m_bBlocking) return m_byEmpty;

	m_timer.start();
	if(!m_socket.waitForReadyRead(WAIT_DELAY)) 
	{
		std::cerr << "Error: Socket timed out while receiving." << std::endl;
		return m_byEmpty;
	}	
	
	int iExpectedMsgLength=0;
	read((char*)&iExpectedMsgLength, 4);
	
	if(iExpectedMsgLength <= 0)
	{
		std::cerr << "Error: Invalid message length: " << iExpectedMsgLength << std::endl;
		return m_byEmpty;
	}

	QByteArray& arrMsg = m_byCurMsg;
	arrMsg.resize(iExpectedMsgLength);
	
	while(m_socket.bytesAvailable() < iExpectedMsgLength)
	{
		if(!m_socket.waitForReadyRead(WAIT_DELAY)) 
		{
			std::cerr << "Error: Socket timed out while receiving." << std::endl;
			return m_byEmpty;
		}
	}
	
	int iRead = read(arrMsg.data(), iExpectedMsgLength);
	if(iRead!=iExpectedMsgLength)
	{
		std::cerr << "Error: Wrong number of bytes received." << std::endl;
		return m_byEmpty;
	}
	
	int iTimeElapsed = m_timer.elapsed();
	if(m_bDebugLog)
		std::cerr << "\033[0;35m" << "[from server] length: " << iExpectedMsgLength << ", time: " << iTimeElapsed << "ms, data: " << arrMsg.data() << "\033[0m" << std::endl;
	
	return arrMsg;
}
////////////////////////////////////////////////////////////////


///////////////////////////// Slots ////////////////////////////
void TcpClient::connected()
{
	if(m_bDebugLog)
		std::cerr << "Connected to server." << std::endl;
}

void TcpClient::disconnected()
{
	if(m_bDebugLog)
		std::cerr << "Disconnected from server." << std::endl;
}

void TcpClient::readReady()
{
	// nur für nichtblockierenden Client erlauben
	if(m_bBlocking) return;
	
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
		}
	}

	// Am Anfang einer Nachricht kommt ein Int, der deren Größe angibt
	if(m_bBeginOfMessage)
	{
		if(iSize < 4) return;
		iSize -= 4;
		
		// Länge der zu erwartenden Nachricht lesen
		m_iExpectedMsgLength = m_iCurMsgLength = 0;
		read((char*)&m_iExpectedMsgLength, 4);
		
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
	
	//std::cout << "Länge: " << iLenRead << ", pcBuf: " << pcBuf << std::endl;
	
	// Ende der gegenwärtigen Nachricht erreicht?
	if(m_iCurMsgLength>=m_iExpectedMsgLength)
	{	
		if(m_iCurMsgLength > m_iExpectedMsgLength)
			std::cerr << "Warning: Got too much data; expected: " << m_iExpectedMsgLength << ", received: " << m_iCurMsgLength << std::endl;
		
		int iTimeElapsed = m_timer.elapsed();
		
		// Fertige Nachricht emittieren
		emit MessageSignal(m_byCurMsg.data(), m_byCurMsg.size());

		if(m_bDebugLog)
			std::cerr << "\033[0;35m" << "[from server] length: " << m_iCurMsgLength << ", time: " << iTimeElapsed << "ms, total: " << m_timer.elapsed() << "ms, data: " << m_byCurMsg.data() << "\033[0m" << std::endl;
		
		// Ende der Nachricht, neue beginnt
		m_bBeginOfMessage = true;
		m_iExpectedMsgLength = m_iCurMsgLength = 0;
	}
}
////////////////////////////////////////////////////////////////

TcpClient::TcpClient(QObject *pParent, bool bBlocking) : QObject(pParent), m_bBlocking(bBlocking), m_socket(pParent), m_bBeginOfMessage(1), m_iCurMsgLength(0), m_bDebugLog(0)
{
	m_iMessageTimeout = -1;	// "-1" bedeutet: Timeout nicht benutzen
	
// Cascade-Qt-Client?
#ifdef __CASCADE_QT_CLIENT__
	bool bUseMessageTimeout = (bool)Config::GetSingleton()->QueryInt("/cascade_config/server/use_message_timeout", 0);
	if(bUseMessageTimeout)
		m_iMessageTimeout = Config::GetSingleton()->QueryInt("/cascade_config/server/message_timeout", 10000); // Default: 10 Sekunden
		
	m_bDebugLog = (bool)Config::GetSingleton()->QueryInt("/cascade_config/server/debug_log", m_bDebugLog);
#else	// Nicos-Client
	m_iMessageTimeout = 5000;
	//m_bDebugLog = true;
#endif
	
	connect(&m_socket, SIGNAL(connected()), this, SLOT(connected()));
	connect(&m_socket, SIGNAL(disconnected()), this, SLOT(disconnected()));
	if(!m_bBlocking) connect(&m_socket, SIGNAL(readyRead()), this, SLOT(readReady()));
}

TcpClient::~TcpClient()
{
	disconnect();
}

void TcpClient::SetDebugLog(bool bLog) { m_bDebugLog = bLog; }
void TcpClient::SetTimeout(int iTimeout) { m_iMessageTimeout = iTimeout; }
