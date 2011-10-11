%Module cascadeclient 0

%Import QtGui/QtGuimod.sip
%Import QtCore/QtCoremod.sip
%Import QtNetwork/QtNetworkmod.sip

%Include ../../nicoswidget/pythonbinding/globals.sip
%Include ../../nicoswidget/pythonbinding/tofloader.sip

class TcpClient : QObject
{
%TypeHeaderCode
#include "../../client.h"
%End

	public:
		TcpClient(QObject* pParent, bool bBlocking);		// bBlocking: use blocking or non-blocking client
		bool connecttohost(const char* pcAddr, int iPort);	// connect to TCP host pcAddr on port iPort
		void disconnect();					// disconnect
		bool isconnected() const;				// are we connected?

		bool sendmsg(const char* pcMsg);			// send message to server
		const QByteArray& recvmsg();				// get message from server

		void SetTimeout(int iTimeout);				// iTimeout < 0  => don't use timeout
};


class NicosClient : TcpClient
{
%TypeHeaderCode
#include "../../nicosclient.h"
%End

	public:
		// calls sendmsg & recvmsg
		const QByteArray& communicate(const char* pcMsg);



		/////////////////////////////////////////////////////////////
		// !!
		// call the setters in Config_TofLoader
		// before using these count methods
		//

		// total counts
		unsigned int counts(const QByteArray& arr);

		// counts inside ROI
		unsigned int counts(const QByteArray& arr, int iStartX, int iEndX, int iStartY, int iEndY);
		/////////////////////////////////////////////////////////////
};
