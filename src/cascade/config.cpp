// *****************************************************************************
// Module:
//   $Id$
//
// Author:
//   Tobias Weber <tweber@frm2.tum.de>
//
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
// *****************************************************************************
// (Singleton-)Klasse zum Einlesen einer XML-Konfigurationsdatei für Cascade

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

Config::Config() : m_pxmldoc(0), m_ppathcontext(0)
{
	xmlInitParser();
	LIBXML_TEST_VERSION
}

Config::~Config()
{
	Clear();
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

int Config::QueryInt(const char* pcXpath, int iDefault)
{
	if(!m_pxmldoc) return iDefault;
	const xmlChar* pxmlPath = xmlCharStrdup(pcXpath);
	
	xmlXPathContextPtr xpathContext = (xmlXPathContextPtr)m_ppathcontext;
	xmlXPathObjectPtr xpathObject = xmlXPathEvalExpression(pxmlPath, xpathContext);
	
	xmlNodeSetPtr pnodeset = xpathObject->nodesetval;
	if(pnodeset->nodeNr==0)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Config: XPath \"" << pcXpath << "\" not found.\n";
		xmlXPathFreeObject(xpathObject);
		return iDefault;
	}
	else if(pnodeset->nodeNr>1)
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "Config: Result for XPath \"" << pcXpath << "\" not unique, using first.\n";
	}
	
	xmlNodePtr pNode = pnodeset->nodeTab[0];
	
	if(!pNode || !pNode->children)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Config: Node for XPath \"" << pcXpath << "\" invalid.\n";
		xmlXPathFreeObject(xpathObject);
		return iDefault;
	}
	
	int iRet = atoi((const char*)pNode->children->content);		// Vorsicht mit diesem Cast!
	xmlXPathFreeObject(xpathObject);
	return iRet;
}

double Config::QueryDouble(const char* pcXpath, double dDefault)
{
	if(!m_pxmldoc) return dDefault;
	const xmlChar* pxmlPath = xmlCharStrdup(pcXpath);
	
	xmlXPathContextPtr xpathContext = (xmlXPathContextPtr)m_ppathcontext;
	xmlXPathObjectPtr xpathObject = xmlXPathEvalExpression(pxmlPath, xpathContext);
	
	xmlNodeSetPtr pnodeset = xpathObject->nodesetval;
	if(pnodeset->nodeNr==0)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Config: XPath \"" << pcXpath << "\" not found.\n";
		xmlXPathFreeObject(xpathObject);
		return dDefault;
	}
	else if(pnodeset->nodeNr>1)
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "Config: Result for XPath \"" << pcXpath << "\" not unique, using first.\n";
	}
	
	xmlNodePtr pNode = pnodeset->nodeTab[0];
	
	if(!pNode || !pNode->children)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Config: Node for XPath \"" << pcXpath << "\" invalid.\n";
		xmlXPathFreeObject(xpathObject);
		return dDefault;
	}
	
	double dRet = dDefault;
	sscanf((const char*)pNode->children->content, "%lf", &dRet); 	// Vorsicht mit diesem Cast!
	xmlXPathFreeObject(xpathObject);
	return dRet;
}

void Config::QueryString(const char* pcXpath, char* pcStr, const char* pcDefault)
{
	if(pcStr!=pcDefault && pcDefault) 
		strcpy(pcStr,pcDefault);
	if(!m_pxmldoc)
		return;
	const xmlChar* pxmlPath = xmlCharStrdup(pcXpath);
	
	xmlXPathContextPtr xpathContext = (xmlXPathContextPtr)m_ppathcontext;
	xmlXPathObjectPtr xpathObject = xmlXPathEvalExpression(pxmlPath, xpathContext);
	
	xmlNodeSetPtr pnodeset = xpathObject->nodesetval;
	if(pnodeset->nodeNr==0)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Config: XPath \"" << pcXpath << "\" not found.\n";
		xmlXPathFreeObject(xpathObject);
		
		return;
	}
	else if(pnodeset->nodeNr>1)
	{
		logger.SetCurLogLevel(LOGLEVEL_WARN);
		logger << "Config: Result for XPath \"" << pcXpath << "\" not unique, using first.\n";
	}
	
	xmlNodePtr pNode = pnodeset->nodeTab[0];
	
	if(!pNode || !pNode->children)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "Config: Node for XPath \"" << pcXpath << "\" invalid.\n";
		xmlXPathFreeObject(xpathObject);
		
		return;
	}
	
	strcpy(pcStr, (const char*)pNode->children->content);
	trim(pcStr);
	xmlXPathFreeObject(xpathObject);
}


//////////////////////////////// Singleton-Zeug ///////////////////////////
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
///////////////////////////////////////////////////////////////////////////

/*int main(void)
{
	Config::GetSingleton()->Load("./cascade.xml");
	std::cout << Config::GetSingleton()->QueryInt("/cascade_config/tof_loader/image_width") << std::endl;
	std::cout << Config::GetSingleton()->QueryInt("/cascade_config/tof_loader/image_height") << std::endl;
	Config::ClearSingleton();
	return 0;
}*/
