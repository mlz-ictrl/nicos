%Module cascadeclient 0

%Import QtGui/QtGuimod.sip
%Import QtCore/QtCoremod.sip
%Import QtNetwork/QtNetworkmod.sip


class TcpClient : QObject
{
%TypeHeaderCode
#include "../../client.h"
%End

	public:
		TcpClient(QObject* pParent, bool bBlocking);
		bool connecttohost(const char* pcAddr, int iPort);
		void disconnect();
		bool isconnected() const;
		
		bool sendmsg(const char* pcMsg);
		const QByteArray& recvmsg();

		void SetDebugLog(bool bLog);
		void SetTimeout(int iTimeout);		// negative Werte schalten Timeout ab
};


class NicosClient : TcpClient 
{
%TypeHeaderCode
#include "../../nicosclient.h"
%End

	public:
		const QByteArray& communicate(const char* pcMsg);
};
