// Im Speicher Daten per Zlib-Deflate dekomprimieren

#include <zlib.h>
#include <iostream>

bool decompress(const char* pcIn, int iLenIn, char* pcOut, int& iLenOut)
{
	z_stream zstr;
	memset(&zstr, 0, sizeof zstr);
	
	zstr.next_in = (Bytef*)pcIn;
	zstr.avail_in = (uInt)iLenIn;
	
	if(inflateInit(&zstr)!=Z_OK) 
	{
		std::cerr << "Konnte Zlib nicht initialisieren." << std::endl;
		return false;
	}
	
	zstr.next_out = (Bytef*)pcOut;
	zstr.avail_out = (uInt)iLenOut;
	
	if(inflate(&zstr, Z_FINISH)!=Z_STREAM_END)
	{
		std::cerr << "Dekompression fehlgeschlagen." << std::endl;
		return false;
	}
	
	iLenOut = (int)zstr.total_out;
	inflateEnd(&zstr);
	
	return true;
}
