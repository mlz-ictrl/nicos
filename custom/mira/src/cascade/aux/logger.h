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

#ifndef __LOGGER__
#define __LOGGER__

#include <sstream>
#include <string>

#define LOGLEVEL_NONE	0
#define LOGLEVEL_ERR	1
#define LOGLEVEL_WARN	2
#define LOGLEVEL_INFO	3

class Logger
{
	protected:
		std::ostream* m_postrLog;
		int m_iLogLevel;
		int m_iCurLogLevel;
		bool m_bOwnsStream;
		std::string m_strCurLog;
		std::string m_strColor;
		bool m_bRepeatLogs;
		std::string m_strLastLog;

		bool IsStdOut() const;
		void Deinit();

		void addlog(const std::string& str);
		void endlog();

	public:
		Logger(const char* pcFile=0);
		virtual ~Logger();

		void log(int iLevel, const char* pcStr);
		void info(const char* pcStr);
		void warning(const char* pcStr);
		void error(const char* pcStr);

		void red(bool bBold=false);
		void green(bool bBold=false);
		void yellow(bool bBold=false);
		void purple(bool bBold=false);
		void normal();

		// the loglevel which controls output
		void SetLogLevel(int iLevel);
		int GetLogLevel() const;

		// the loglevel for logs using operator <<
		void SetCurLogLevel(int iLevel);
		int GetCurLogLevel() const;

		void SetRepeatLogs(bool bRepeat);

		// pcFile==0 => use stderr
		void Init(const char* pcFile=0);

		template<class T> friend Logger& operator<< (Logger& log, const T& t);
};

template<class T> Logger& operator<< (Logger& log, const T& t)
{
	std::ostringstream ostr;
	ostr << t;
	log.addlog(ostr.str());
	return log;
}

extern Logger logger;

#endif
