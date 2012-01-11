// *****************************************************************************
// NICOS-NG, the Networked Instrument Control System of the FRM-II
// Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
// (singleton) class for reading xml configuration files

#include "config.h"

#include <iostream>
#include <stdlib.h>
#include <string.h>

#include <libxml/tree.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <libxml/xpathInternals.h>

#include "logger.h"
#include "helper.h"

#if !defined(LIBXML_XPATH_ENABLED) || !defined(LIBXML_SAX1_ENABLED)
	#error "Fehler: libxml mit XPath benötigt."
#endif

int Config::s_iInstances = 0;

Config::Config() : m_pxmldoc(0), m_ppathcontext(0)
{
	if(s_iInstances == 0)
	{
		xmlInitParser();
		LIBXML_TEST_VERSION
	}
	++s_iInstances;
}

Config::~Config()
{
	Clear();

	--s_iInstances;
	if(s_iInstances == 0)
		xmlCleanupParser();
}

void Config::Clear()
{
	if(m_ppathcontext)
	{
		xmlXPathFreeContext((xmlXPathContextPtr)m_ppathcontext);
		m_ppathcontext = 0;
	}

	if(m_pxmldoc)
	{
		xmlFreeDoc((xmlDoc*)m_pxmldoc);
		m_pxmldoc = 0;
	}
}

bool Config::Load(const char* pcFile)
{
	Clear();

	m_pxmldoc = xmlParseFile(pcFile);
	if(!m_pxmldoc)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Config: Could not load XML file \"" << pcFile << "\".\n";
		return false;
	}
	m_ppathcontext = xmlXPathNewContext((xmlDoc*)m_pxmldoc);
	return true;
}

int Config::QueryInt(const char* pcXpath, int iDefault, bool* pOK)
{
	if(!m_pxmldoc)
	{
		if(pOK) *pOK=false;
		return iDefault;
	}
	const xmlChar* pxmlPath = xmlCharStrdup(pcXpath);

	xmlXPathContextPtr xpathContext = (xmlXPathContextPtr)m_ppathcontext;
	xmlXPathObjectPtr xpathObject = xmlXPathEvalExpression(pxmlPath,
														   xpathContext);

	xmlNodeSetPtr pnodeset = xpathObject->nodesetval;
	if(pnodeset->nodeNr==0)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Config: XPath \"" << pcXpath << "\" not found.\n";
		xmlXPathFreeObject(xpathObject);

		if(pOK) *pOK=false;
		return iDefault;
	}
	else if(pnodeset->nodeNr>1)
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "Config: Result for XPath \"" << pcXpath
			   << "\" not unique, using first.\n";
	}

	xmlNodePtr pNode = pnodeset->nodeTab[0];

	if(!pNode || !pNode->children)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Config: Node for XPath \"" << pcXpath << "\" invalid.\n";
		xmlXPathFreeObject(xpathObject);

		if(pOK) *pOK=false;
		return iDefault;
	}

	// Vorsicht mit diesem Cast!
	int iRet = atoi((const char*)pNode->children->content);
	xmlXPathFreeObject(xpathObject);

	if(pOK) *pOK=true;
	return iRet;
}

double Config::QueryDouble(const char* pcXpath, double dDefault, bool* pOK)
{
	if(!m_pxmldoc)
	{
		if(pOK) *pOK=false;
		return dDefault;
	}
	const xmlChar* pxmlPath = xmlCharStrdup(pcXpath);

	xmlXPathContextPtr xpathContext = (xmlXPathContextPtr)m_ppathcontext;
	xmlXPathObjectPtr xpathObject = xmlXPathEvalExpression(pxmlPath,
																xpathContext);

	xmlNodeSetPtr pnodeset = xpathObject->nodesetval;
	if(pnodeset->nodeNr==0)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Config: XPath \"" << pcXpath << "\" not found.\n";
		xmlXPathFreeObject(xpathObject);

		if(pOK) *pOK=false;
		return dDefault;
	}
	else if(pnodeset->nodeNr>1)
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "Config: Result for XPath \"" << pcXpath
			   << "\" not unique, using first.\n";
	}

	xmlNodePtr pNode = pnodeset->nodeTab[0];

	if(!pNode || !pNode->children)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Config: Node for XPath \"" << pcXpath << "\" invalid.\n";
		xmlXPathFreeObject(xpathObject);

		if(pOK) *pOK=false;
		return dDefault;
	}

	double dRet = dDefault;
	// Vorsicht mit diesem Cast!
	sscanf((const char*)pNode->children->content, "%lf", &dRet);
	xmlXPathFreeObject(xpathObject);

	if(pOK) *pOK=true;
	return dRet;
}

std::string Config::QueryString(const char* pcXpath, const char* pcDefault,
								bool* pOK)
{
	std::string strRet;

	if(pcDefault)
	{
		strRet = pcDefault;
		strRet = trim(strRet);
	}

	if(!m_pxmldoc)
	{
		if(pOK) *pOK=false;
		return strRet;
	}

	const xmlChar* pxmlPath = xmlCharStrdup(pcXpath);

	xmlXPathContextPtr xpathContext = (xmlXPathContextPtr)m_ppathcontext;
	xmlXPathObjectPtr xpathObject = xmlXPathEvalExpression(pxmlPath,
															xpathContext);

	xmlNodeSetPtr pnodeset = xpathObject->nodesetval;

	if(pnodeset->nodeNr==0)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Config: XPath \"" << pcXpath << "\" not found.\n";
		xmlXPathFreeObject(xpathObject);

		if(pOK) *pOK=false;
		return strRet;
	}
	else if(pnodeset->nodeNr>1)
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "Config: Result for XPath \"" << pcXpath
			   << "\" not unique, using first.\n";
	}

	xmlNodePtr pNode = pnodeset->nodeTab[0];

	if(!pNode || !pNode->children)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Config: Node for XPath \"" << pcXpath << "\" invalid.\n";
		xmlXPathFreeObject(xpathObject);

		if(pOK) *pOK=false;
		return strRet;
	}

	strRet = (const char*)pNode->children->content;
	strRet = trim(strRet);

	xmlXPathFreeObject(xpathObject);

	if(pOK) *pOK=true;
	return strRet;
}


//////////////////////////////// Singleton-Zeug ////////////////////////////////
Config *Config::s_pConfig = 0;

Config* Config::GetSingleton()
{
	if(!s_pConfig) s_pConfig = new Config();
	return s_pConfig;
}

void Config::ClearSingleton()
{
	if(s_pConfig)
	{
		delete s_pConfig;
		s_pConfig = 0;
	}
}
////////////////////////////////////////////////////////////////////////////////

/*int main(void)
{
	Config::GetSingleton()->Load("./cascade.xml");
	std::cout << Config::GetSingleton()->QueryInt(
	 					"/cascade_config/tof_loader/image_width") << std::endl;
	std::cout << Config::GetSingleton()->QueryInt(
	 					"/cascade_config/tof_loader/image_height") << std::endl;
	Config::ClearSingleton();
	return 0;
}*/
