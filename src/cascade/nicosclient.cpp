#include <iostream>

#include "nicosclient.h"
#include "tofloader.h"


NicosClient::NicosClient()
{
	Config_TofLoader::Init();
}

NicosClient::~NicosClient()
{
	Config_TofLoader::Deinit();
}

const QByteArray& NicosClient::communicate(const char* pcMsg)
{
	m_mutex.lock();
	
	sendmsg(pcMsg);
	const QByteArray& arr = recvmsg();
	
	m_mutex.unlock();
	return arr;
}


/*int main(int argc, char** argv)
{
	NicosClient client;
	if(!client.connecttohost("cascade7.reseda.frm2", 1234))
		return -1;
	
	client.sendmsg("CMD_status");
	char pcMsgBuf[256];
	client.recvmsg(pcMsgBuf, sizeof pcMsgBuf);
	std::cout << pcMsgBuf << std::endl;
	
	client.disconnect();
	return 0;
}*/
