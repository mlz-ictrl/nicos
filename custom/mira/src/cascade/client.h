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

#ifndef __TCP_CLIENT__
#define __TCP_CLIENT__

#include <QtGui/QApplication>
#include <QtCore/QObject>
#include <QtCore/QTimer>
#include <QtNetwork/QtNetwork>
#include <QtNetwork/QTcpServer>
#include <QtNetwork/QTcpSocket>

/*
 * TCP client usable in blocking and non-blocking mode
 * msg protocol: 4 Bytes (int): size of message followed by message
 */
class TcpClient : public QObject
{
Q_OBJECT
	protected:
		bool m_bBlocking;
		QTcpSocket m_socket;

		const QByteArray m_byEmpty;
		/////////////// gegenwärtige Nachricht //////////////////////
		QByteArray m_byCurMsg;
		bool m_bBeginOfMessage;
		int m_iExpectedMsgLength;
		int m_iCurMsgLength;
		int m_iMessageTimeout;
		QTime m_timer;
		/////////////////////////////////////////////////////////////

		// internal methods which read and send raw data in disregard of the
		// protocol
		int read(char* pcData, int iLen);
		bool write(const char* pcBuf, int iSize, bool bIsBinary=false);
		bool sendfile(const char* pcFileName);

	public:
		TcpClient(QObject *pParent=0, bool bBlocking=true);
		virtual ~TcpClient();

		// connect to server pcAddr at port iPort
		bool connecttohost(const char* pcAddr, int iPort);
		void disconnect();
		bool isconnected() const;

		// send a message to the server
		bool sendmsg(const char* pcMsg);

		// only for blocking client
		const QByteArray& recvmsg(void);

		// negative values disable timeout
		void SetTimeout(int iTimeout);

	signals:
		// this signal is emitted by the nonblocking client
		// if a complete message is available
		void MessageSignal(const char* pcBuf, int iLen);

	protected slots:
		void connected();
		void disconnected();

		// only for NONblocking client
		void readReady();
};

#endif
