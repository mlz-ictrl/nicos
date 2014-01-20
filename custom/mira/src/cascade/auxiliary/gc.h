// *****************************************************************************
// NICOS, the Networked Instrument Control System of the FRM-II
// Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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

#include <map>
#include <vector>
#include <string>

#ifndef __CASC_GC__
#define __CASC_GC__

struct Gc_info
{
	void *pvMem;
	unsigned int iLen;
	int iRefs;
	std::string strDesc;

	Gc_info();
};

/**
 * \brief Garbage Collector
 */
class Gc
{
	protected:
		typedef std::map<void*, Gc_info> t_map;
		t_map m_map;

		/// clean everything
		void kill();

	public:
		Gc();
		virtual ~Gc();

		/// release unreferenced mem
		void gc();

		/// allocate mem
		void* malloc(unsigned int uiSize, const char* pcDesc=0);

		/// add a mem reference
		bool acquire(void* pv);

		/// release a mem reference
		bool release(void* pv);

		/// total memory allocated
		unsigned int memsize() const;

		void sanity_check() const;
		void print() const;
		
		std::vector<Gc_info> get_elems() const;
};

extern Gc gc;

#endif
