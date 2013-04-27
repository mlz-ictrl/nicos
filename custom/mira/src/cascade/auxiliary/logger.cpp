// *****************************************************************************
// NICOS, the Networked Instrument Control System of the FRM-II
// Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

#include <time.h>
#include <string>
#include <sstream>
#include <algorithm>
#include <fstream>
#include <iostream>
#include "logger.h"

Logger::Logger(const char* pcFile) : m_postrLog(0), m_iLogLevel(LOGLEVEL_INFO),
									 m_iCurLogLevel(LOGLEVEL_INFO),
									 m_bOwnsStream(0), m_bRepeatLogs(0)
{
	Init(pcFile);
}

Logger::~Logger()
{
	Deinit();
}

void Logger::Deinit()
{
	if(m_bOwnsStream && m_postrLog)
		delete m_postrLog;
	m_postrLog = 0;
}

void Logger::Init(const char* pcFile)
{
	Deinit();

	if(pcFile)
	{
		m_postrLog = new std::ofstream(pcFile);
		if(((std::ofstream*)m_postrLog)->is_open())
		{
			m_bOwnsStream = 1;
		}
		else
		{
			delete m_postrLog;
			m_postrLog = &std::cerr;
			m_bOwnsStream = 0;
		}
	}
	else
	{
		m_postrLog = &std::cerr;
		m_bOwnsStream = 0;
	}
}

void Logger::addlog(const std::string& str)
{
	size_t iPos = str.find('\n');
	if(iPos != std::string::npos)
	{
		std::string strA = str.substr(0,iPos);
		std::string strB = str.substr(iPos+1);

		m_strCurLog += strA;
		endlog();

		addlog(strB);
	}
	else
	{
		m_strCurLog += str;
	}
}

void Logger::endlog()
{
	log(GetCurLogLevel(), m_strCurLog.c_str());
	m_strCurLog = "";
}

bool Logger::IsStdOut() const
{
	return (m_postrLog==&std::cerr) || (m_postrLog==&std::cout);
}

void Logger::red(bool bBold)
{
	m_strColor = bBold ? "\033[1;31m" : "\033[0;31m";
}

void Logger::green(bool bBold)
{
	m_strColor = bBold ? "\033[1;32m" : "\033[0;32m";
}

void Logger::yellow(bool bBold)
{
	m_strColor = bBold ? "\033[1;33m" : "\033[0;33m";
}

void Logger::purple(bool bBold)
{
	m_strColor = bBold ? "\033[1;35m" : "\033[0;35m";
}

void Logger::normal()
{
	m_strColor = "";
}

void Logger::log(int iLevel, const char* pcStr)
{
	// repeat duplicate message?
	if(m_strLastLog == pcStr && !m_bRepeatLogs)
		return;

	if(!m_postrLog) return;
	if(iLevel > m_iLogLevel) return;

	// only log time when not writing to stdout
	std::string strTime = "";
	if(!IsStdOut())
	{
		time_t tm;
		time(&tm);
		strTime = ctime (&tm);
		std::replace(strTime.begin(), strTime.end(), '\n', ' ');
	}

	std::string strLevel = "";
	switch(iLevel)
	{
		case LOGLEVEL_ERR:
		{
			red(true);
			strLevel = "ERROR: ";
			break;
		}
		case LOGLEVEL_WARN:
		{
			purple(true);
			strLevel = "WARNING: ";
			break;
		}
		/*case LOGLEVEL_INFO:
		{
			strLevel = "INFO: ";
			break;
		}*/
	}

	if(IsStdOut() && m_strColor!="")
		(*m_postrLog) << m_strColor;

	(*m_postrLog) << strTime << strLevel << pcStr;

	if(IsStdOut() && m_strColor!="")
		(*m_postrLog) << "\033[0m";

	normal();
	(*m_postrLog) << std::endl;

	m_strLastLog = pcStr;
}

void Logger::info(const char* pcStr)
{
	log(LOGLEVEL_INFO, pcStr);
}

void Logger::warning(const char* pcStr)
{
	log(LOGLEVEL_WARN, pcStr);
}

void Logger::error(const char* pcStr)
{
	log(LOGLEVEL_ERR, pcStr);
}

void Logger::SetLogLevel(int iLevel) { m_iLogLevel = iLevel; }
int Logger::GetLogLevel() const { return m_iLogLevel; }

void Logger::SetCurLogLevel(int iLevel) { m_iCurLogLevel = iLevel; }
int Logger::GetCurLogLevel() const { return m_iCurLogLevel; }

void Logger::SetRepeatLogs(bool bRepeat) { m_bRepeatLogs = bRepeat; }


Logger logger;
