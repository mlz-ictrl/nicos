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


#ifndef __CASCADE_HELPER__
#define __CASCADE_HELPER__

#include <string>
#include <ostream>
#include <fstream>
#include <sstream>
#include <limits>
#include <algorithm>
#include <zlib.h>
#include "logger.h"

//------------------------------------------------------------------------------

/**
 * \brief cleanup class
 * which automatically calls a deinit method when going out of scope
 */
template<class T> class cleanup
{
	protected:
		T& m_t;
		void (T::*m_pDeinit)();

	public:
		cleanup(T& t, void (T::*pDeinit)()) : m_t(t), m_pDeinit(pDeinit) {}
		virtual ~cleanup(){ (m_t.*m_pDeinit)(); }

};


/// deletes an object when going out of scope
template<class T> class autodeleter
{
protected:
	T *m_t;
	bool m_bIsArray;

public:
	autodeleter(T* t, bool bIsArray=false) : m_t(t), m_bIsArray(bIsArray)
	{}

	~autodeleter()
	{
		if(m_t)
		{
			if(m_bIsArray)
				delete[] m_t;
			else
				delete m_t;
			m_t = 0;
		}
	}
};

//------------------------------------------------------------------------------

/// file size
long GetFileSize(FILE* pf);
long GetFileSize(const char* pcFileName);

std::string GetFileEnding(const char* pcFileName);

std::pair<std::string, std::string>
split(const std::string& str, const std::string& splitter);

//------------------------------------------------------------------------------



//------------------------------------------------------------------------------


/// remove whitespaces at the beginning and the end of a string
void trim(char* pcStr);
std::string trim(const std::string& str);

std::string get_byte_str(unsigned int iSize);

void find_and_replace(std::string& str1, const std::string& str_old,
					  const std::string& str_new);

//------------------------------------------------------------------------------


/// convert big endian to little endian and vice versa
unsigned int endian_swap(unsigned int ui);


//------------------------------------------------------------------------------


template<typename T> bool float_equal(T t1, T t2)
{
	T tdiff = t2-t1;
	if(tdiff < T(0))
		tdiff = -tdiff;
	
	if(tdiff < std::numeric_limits<T>::epsilon())
		return true;
	return false;
}

//------------------------------------------------------------------------------

/// group numbers, e.g.: 123 456 789
void SetNumberGrouping(std::ostream& ostr);


//------------------------------------------------------------------------------

double safe_log10(double d);
double safe_log10_lowerrange(double d);


//------------------------------------------------------------------------------


/// random number between 0 and 1
double rand01();
/// random number between -1 and 1
double randmp1();


//------------------------------------------------------------------------------


template<typename T> void save_dat(const char* pcFile,
									const T* pDataOut,
									unsigned int iSize,
									bool bErrs=false)
{
	static unsigned int uiCnt = 0;
	std::ostringstream ostr;
	
	if(pcFile==0)
	{
		ostr << "tmp_" << uiCnt++ << ".dat";
		pcFile = ostr.str().c_str();
	}

	std::ofstream ofstr(pcFile);
	if(!ofstr.is_open())
		return;

	for(unsigned int i=0; i<iSize; ++i)
	{
		ofstr << i << "\t" << pDataOut[i];
		if(bErrs) ofstr << "\t" << sqrt(pDataOut[i]);
		ofstr << "\n";
	}

	ofstr.close();
}

//------------------------------------------------------------------------------

template<typename T> T sum(const T* first, const T* last)
{
	T tsum = 0;

	for(const T* pt=first; pt!=last; ++pt)
		tsum += *pt;

	return tsum;
}

//-----------------------------------------------------------------------------



bool zlib_decompress(const char* pcIn, int iLenIn, char* pcOut, int& iLenOut);
bool gz_decompress(const void* pvIn, unsigned int iLenIn, void*& pvOut, unsigned int& iLenOut);
bool IsGZ(const void* pvMem);
bool IsGZFile(const char* pcFile);
unsigned int GetGZFileSize(const char* pcFile);

//-----------------------------------------------------------------------------

#endif
