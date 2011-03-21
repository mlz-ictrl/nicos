// (Singleton-)Klasse zum Einlesen einer XML-Konfigurationsdatei für Cascade

#ifndef __CASCADE_CONFIG__
#define __CASCADE_CONFIG__

class Config
{
	private:
		static Config *s_pConfig;
		
		Config();
		virtual ~Config();
	
	protected:
		void *m_pxmldoc;
		void *m_ppathcontext;
		void Clear();
		
	public:
		bool Load(const char* pcFile);
		
		int QueryInt(const char* pcXpath, int iDefault=0);
		double QueryDouble(const char* pcXpath, double dDefault=0.);
		void QueryString(const char* pcXpath, char* pcStr, const char* pcDefault);
		
		static Config* GetSingleton();
		static void ClearSingleton();
};

#endif
