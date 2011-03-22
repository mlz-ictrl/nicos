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

#ifndef __TCP_CLIENT__
#define __TCP_CLIENT__

#include <QtGui/QApplication>
#include <QtCore/QObject>
#include <QtCore/QTimer>
#include <QtNetwork/QtNetwork>
#include <QtNetwork/QTcpServer>
#include <QtNetwork/QTcpSocket>

class TcpClient : public QObject
{
Q_OBJECT
	protected:
		bool m_bBlocking;
		QTcpSocket m_socket;
		
		/////////////// gegenwärtige Nachricht //////////////////////
		QByteArray m_byCurMsg;
		bool m_bBeginOfMessage;
		int m_iExpectedMsgLength;
		int m_iCurMsgLength;
		int m_iMessageTimeout;
		QTime m_timer;
		/////////////////////////////////////////////////////////////
		
		bool m_bDebugLog;
		
		int read(char* pcData, int iLen);
		bool write(const char* pcBuf, int iSize);

	public:
		TcpClient(QObject *pParent=0, bool bBlocking=true);
		virtual ~TcpClient();
		
		bool connecttohost(const char* pcAddr, int iPort);
		void disconnect();
		bool isconnected() const;
		
		bool sendfile(const char* pcFileName);
		bool sendmsg(const char* pcMsg);
		const QByteArray& recvmsg(void);	// nur für blockierenden Client
		
		void SetDebugLog(bool bLog);
		void SetTimeout(int iTimeout);		// negative Werte schalten Timeout ab
		
	signals:
		// Signal, das der nichtblockierende Client emittiert, wenn eine vollständige Nachricht da ist
		void MessageSignal(const char* pcBuf, int iLen);

	protected slots:
		void connected();
		void disconnected();
		void readReady();			// nur für NICHTblockierenden Client
};

#endif
