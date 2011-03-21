#ifndef __NICOSCLIENT__
#define __NICOSCLIENT__

#include <QMutex>
#include "client.h" 


class NicosClient : public TcpClient
{
	protected:
		QMutex m_mutex;
	
	public:
		NicosClient();
		virtual ~NicosClient();
		
		const QByteArray& communicate(const char* pcMsg);
};

#endif
