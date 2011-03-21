// blockierend und nichtblockierend nutzbarer TCP-Client
// "Protokoll": 4 Bytes (int) = Größe der Nachricht; Nachricht

#include "client.h"
#include <iostream>
#include <stdlib.h>
#include "config.h"

#define WAIT_DELAY 5000

/////////////////////// Verbindung /////////////////////////////
bool TcpClient::connecttohost(const char* pcAddr, int iPort)
{
	disconnect();
	
	// Namen auflösen
	QHostInfo info = QHostInfo::fromName(pcAddr);
	if(info.addresses().isEmpty())
	{
		std::cerr << "Fehler: Konnte " << pcAddr << " nicht auflösen." << std::endl;
		return false;
	}
	QHostAddress address = info.addresses().first();
	/*QHostAddress address = QHostAddress(QString(pcAddr))*/ 
	
	// Verbinden
	m_socket.connectToHost(address, quint16(iPort));
	bool bConnected = m_socket.waitForConnected(WAIT_DELAY);
	
	if(!bConnected)
		std::cerr << "Fehler: Konnte nicht mit " << pcAddr << " an Port " << iPort << " verbinden." << std::endl;

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
	// Fehler im Server: Sollte eigentlich nicht 0-terminiert werden müssen
	int iLen = strlen(pcMsg)+1;
	
	// Länge der folgenden Nachricht übertragen
	write((char*)&iLen, 4);
	
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
		std::cerr << "\033[0;31m" << "[an Server] Länge: " << iSize << ", Daten: " << pcBuf << "\033[0m" << std::endl;

	return true;
}

bool TcpClient::sendfile(const char* pcFileName)
{
	std::cerr << "Sende \"" << pcFileName << "\"" << std::endl;
	FILE *pf = fopen(pcFileName,"rb");
	if(!pf)
	{ 
		std::cerr << "Konnte Datei \"" << pcFileName << "\" nicht oeffnen." << std::endl;
		return false;
	}
	
	// Größe der Datei herausbekommen
	fseek(pf, 0, SEEK_END);
	long iSize = ftell(pf);
	fseek(pf, 0, SEEK_SET);
	
	char *pcDaten = new char[iSize];
	if(!fread(pcDaten, 1, iSize, pf))
	{
		std::cerr << "Fehler beim Lesen der Datei \"" << pcFileName << "\"." << std::endl;
		fclose(pf);
		delete[] pcDaten;
		return false;
	}
	fclose(pf);
	if(!write((char*)pcDaten,iSize))
		std::cerr << "Fehler beim Senden der Datei \"" << pcFileName << "\"." << std::endl;
	delete[] pcDaten;
	
	std::cerr << iSize << " Bytes gesendet." << std::endl;
	return true;
}
////////////////////////////////////////////////////////////////


///////////////////////// lesen ////////////////////////////////
int TcpClient::read(char* pcData, int iLen)
{
	int iLenRead = m_socket.read(pcData, iLen);
	if(iLenRead<0)
	{
		std::cerr << "Fehler beim Lesen des Sockets." << std::endl;
		iLenRead = 0;
	}
	return iLenRead;
}

const QByteArray& TcpClient::recvmsg(void)
{
	static const QByteArray arrError = QByteArray("");
	
	// nur für blockierenden Client erlauben
	if(!m_bBlocking) return arrError;

	m_timer.start();
	if(!m_socket.waitForReadyRead(WAIT_DELAY)) 
	{
		std::cerr << "Fehler: Socket-Timeout beim Datenempfang." << std::endl;
		return arrError;
	}	
	
	int iExpectedMsgLength=0;
	read((char*)&iExpectedMsgLength, 4);
	
	if(iExpectedMsgLength <= 0)
	{
		std::cerr << "Fehler: Ungültige Nachrichtenlänge: " << iExpectedMsgLength << std::endl;
		return arrError;
	}

	QByteArray& arrMsg = m_byCurMsg;
	arrMsg.resize(iExpectedMsgLength);
	
	while(m_socket.bytesAvailable() < iExpectedMsgLength)
	{
		if(!m_socket.waitForReadyRead(WAIT_DELAY)) 
		{
			std::cerr << "Fehler: Socket-Timeout beim Datenempfang." << std::endl;
			return arrError;
		}
	}
	
	int iRead = read(arrMsg.data(), iExpectedMsgLength);
	if(iRead!=iExpectedMsgLength)
	{
		std::cerr << "Fehler: Falsche Anzahl an Bytes empfangen." << std::endl;
		return arrError;
	}
	
	int iTimeElapsed = m_timer.elapsed();
	if(m_bDebugLog)
		std::cerr << "\033[0;35m" << "[von Server] Länge: " << iExpectedMsgLength << ", Empfangszeit: " << iTimeElapsed << "ms, Daten: " << arrMsg.data() << "\033[0m" << std::endl;
	
	return arrMsg;
}
////////////////////////////////////////////////////////////////


///////////////////////////// Slots ////////////////////////////
void TcpClient::connected()
{
	if(m_bDebugLog)
		std::cerr << "Verbunden mit Server." << std::endl;
}

void TcpClient::disconnected()
{
	if(m_bDebugLog)
		std::cerr << "Verbindung von Server getrennt." << std::endl;
}

void TcpClient::readReady()
{
	// nur für nichtblockierenden Client erlauben
	if(m_pReadCB==0 || m_bBlocking) return;
	
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
		//std::cerr << "Nachrichtenstart" << std::endl;
		
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
			std::cerr << "Zuviele Daten empfangen; erwartet: " << m_iExpectedMsgLength << ", bekommen: " << m_iCurMsgLength << std::endl;
		
		int iTimeElapsed = m_timer.elapsed();
		
		// Fertige Nachricht an Hauptfenster senden
		m_pReadCB(m_byCurMsg.data(), m_byCurMsg.size(), m_pvUser);

		if(m_bDebugLog)
			std::cerr << "\033[0;35m" << "[von Server] Länge: " << m_iCurMsgLength << ", Empfangszeit: " << iTimeElapsed << "ms, Gesamt: " << m_timer.elapsed() << "ms, Daten: " << m_byCurMsg.data() << "\033[0m" << std::endl;
		
		// Ende der Nachricht, neue beginnt
		m_bBeginOfMessage = true;		
		m_iExpectedMsgLength = m_iCurMsgLength = 0;
	}
}
////////////////////////////////////////////////////////////////

TcpClient::TcpClient(QObject *pParent, void (*pReadCB)(char*, int, void*), void* pvUser) : QObject(pParent), m_socket(pParent), m_pReadCB(pReadCB), m_pvUser(pvUser), m_bBeginOfMessage(1), m_iCurMsgLength(0), m_bDebugLog(0)
{
	// Wenn kein Callback angegeben wurde, blockierenden Client verwenden
	m_bBlocking=0;
	if(pReadCB==0) m_bBlocking=1;
	
	m_iMessageTimeout = -1;	// "-1" bedeutet: Timeout nicht benutzen
	
// Cascade-Qt-Client?
#ifdef __CASCADE_QT_CLIENT__
	bool bUseMessageTimeout = (bool)Config::GetSingleton()->QueryInt("/cascade_config/server/use_message_timeout", 0);
	if(bUseMessageTimeout)
		m_iMessageTimeout = Config::GetSingleton()->QueryInt("/cascade_config/server/message_timeout", 10000); // Default: 10 Sekunden
		
	m_bDebugLog = (bool)Config::GetSingleton()->QueryInt("/cascade_config/server/debug_log", m_bDebugLog);
#else	// Minuit-Client
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

#ifdef __CASCADE_QT_CLIENT__
	// Qt-Metaobjekte
	#include "client.moc"
#endif
