// einfache Argumentstrings der Sorte "status=1 error=0" lesen und eine Hashmap daraus machen

#ifndef __PRIMITIV_PARSER__
#define __PRIMITIV_PARSER__

#include <stdlib.h>
#include <string>
#include <map>
#include <sstream>

class ArgumentMap
{
	protected:
		std::map<std::string, std::string> m_mapArgs;
		
	public:
		//////////////// Neue Wertepaare (z.B. "status=1 error=0") hinzufügen ///////////
		void add(const char* pcStr)
		{
			std::istringstream istr(pcStr);
			
			while(!istr.eof())
			{
				std::string str;
				istr >> str;
		
				int iPos = str.find("=");
				if(iPos == std::string::npos)
				{
					std::cerr << "Fehler beim Parsen des Strings: \"" << pcStr << "\"" << std::endl;
					break;
				}
				
				// links des Gleichheitszeichens
				std::string strLinks = str.substr(0,iPos);
				
				// rechts des Gleichheitszeichens
				std::string strRechts = str.substr(iPos+1, str.length()-iPos-1);;
				m_mapArgs.insert(std::pair<std::string,std::string>(strLinks, strRechts));
				
				//std::cout << "Links: \"" << strLinks << "\", Rechts: \"" << strRechts << "\"" << std::endl;
			}
		}
		/////////////////////////////////////////////////////////////////////////////////
		
		/////////////////////////////// Werte abfragen /////////////////////////////
		const char* QueryString(const char* pcKey) const
		{
			std::map<std::string,std::string>::const_iterator iter = m_mapArgs.find(pcKey);
			if(iter == m_mapArgs.end())
				return 0;
			return iter->second.c_str();
		}
		
		int QueryInt(const char* pcKey, int iDefault=0) const
		{
			const char* pcStr = QueryString(pcKey);
			if(pcStr==NULL) return iDefault;
			
			return atoi(pcStr);
		}
		////////////////////////////////////////////////////////////////////////////
		
		
		ArgumentMap(const char* pcStr)
		{
			add(pcStr);
		}
	
		virtual ~ArgumentMap()
		{}
};

#endif
