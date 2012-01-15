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

#include "gc.h"
#include "logger.h"
#include <stdlib.h>
#include <iostream>


Gc_info::Gc_info() : iLen(0), iRefs(0)
{}


Gc::Gc() {}

Gc::~Gc() { kill(); }

void Gc::kill()
{
	for(t_map::iterator iter=m_map.begin(); iter!=m_map.end(); ++iter)
	{
		if((*iter).first)
			free((*iter).first);
		m_map.erase(iter--);
	}
}

void Gc::gc()
{
	for(t_map::iterator iter=m_map.begin(); iter!=m_map.end(); ++iter)
	{
		void *pv = (*iter).first;
		Gc_info& info = (*iter).second;
		if(info.iRefs > 0)
			continue;

		if(pv)
			free(pv);
		m_map.erase(iter--);
	}
}

void* Gc::malloc(unsigned int uiSize)
{
	void* pv = ::malloc(uiSize);

	if(pv==0)
	{
		logger.SetCurLogLevel(LOGLEVEL_ERR);
		logger << "gc: Memory could not be allocated. "
				<< "Requested size: " << uiSize << "\n";

		return 0;
	}

	Gc_info gci;
	gci.iLen = uiSize;
	++gci.iRefs;
	m_map.insert(t_map::value_type(pv, gci));

	return pv;
}

bool Gc::acquire(void* pv)
{
	if(pv==0)
	{
		//logger.SetCurLogLevel(LOGLEVEL_WARN);
		//logger << "gc: Tried to aquire NULL.\n";
		return false;
	}

	t_map::iterator iter = m_map.find(pv);
	if(iter == m_map.end())
	{
		//logger.SetCurLogLevel(LOGLEVEL_WARN);
		//logger << "gc: Tried to aquire unreferenced mem.\n";
		return false;
	}

	++(*iter).second.iRefs;
	return true;
}

bool Gc::release(void* pv)
{
	if(pv==0)
	{
		//logger.SetCurLogLevel(LOGLEVEL_WARN);
		//logger << "gc: Tried to release NULL.\n";
		return false;
	}

	t_map::iterator iter = m_map.find(pv);
	if(iter == m_map.end())
	{
		//logger.SetCurLogLevel(LOGLEVEL_WARN);
		//logger << "gc: Tried to release unreferenced mem.\n";

		return false;
	}

	--(*iter).second.iRefs;
	if((*iter).second.iRefs == 0)
	{
		if((*iter).first)
			free((*iter).first);

		m_map.erase(iter);
	}
	return true;
}

void Gc::print() const
{
	if(m_map.size()==0)
	{
		logger.SetCurLogLevel(LOGLEVEL_INFO);
		logger << "gc: Clean.\n";
	}

	for(t_map::const_iterator iter=m_map.begin(); iter!=m_map.end(); ++iter)
	{
		void *pv = (*iter).first;
		const Gc_info& info = (*iter).second;

		logger.SetCurLogLevel(LOGLEVEL_INFO);
		logger << "gc: mem=" << std::hex << pv
			   << ", len=" << std::dec << info.iLen
			   << ", refs=" << info.iRefs
			   << ".\n";
	}
}

Gc gc;


/*
int main()
{
	Gc gc;
	void *pv = gc.malloc(10);
	void *pv1 = gc.malloc(100);

	gc.acquire(pv);
	gc.release(pv);
	gc.release(pv);
	gc.print();

	return 0;
}
*/
