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
		
		////////////////////// Callback ////////////////////////////////////
		////////////////////// (nichtblockierender Client) /////////////////
		void (*m_pReadCB)(char* pcBuf, int iLen, void* pvUser); // Callback, an das neu verfügbare Daten gesendet werden
		void *m_pvUser;						// this-Pointer auf Cascade-Objekt
		////////////////////////////////////////////////////////////////////
		
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
		// Callback-Funktion hier übergeben => wählt die nichtblockierende Version aus
		TcpClient(QObject *pParent=0, void (*pReadCB)(char*, int, void*)=0, void* pvUser=0);
		virtual ~TcpClient();
		
		bool connecttohost(const char* pcAddr, int iPort);
		void disconnect();
		bool isconnected() const;
		
		bool sendfile(const char* pcFileName);
		bool sendmsg(const char* pcMsg);
		const QByteArray& recvmsg(void);	// nur für blockierenden Client
		
		void SetDebugLog(bool bLog);
		void SetTimeout(int iTimeout);		// negative Werte schalten Timeout ab

	protected slots:
		void connected();
		void disconnected();
		void readReady();			// nur für NICHTblockierenden Client
};

#endif
