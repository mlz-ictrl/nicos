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


#ifndef __CASCADE_HELPER__
#define __CASCADE_HELPER__

// substitution for missing __try ... __finally support in gcc
template<class T> class cleanup
{
	protected:
		T& m_t;
		void (T::*m_pDeinit)();
	
	public:
		cleanup(T& t, void (T::*pDeinit)()) : m_t(t), m_pDeinit(pDeinit) {}
		virtual ~cleanup() { (m_t.*m_pDeinit)(); }
};

#endif
