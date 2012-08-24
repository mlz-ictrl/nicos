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

#ifndef __VEC2d__
#define __VEC2d__

#include <iostream>
#include <math.h>

/*
 * 2D vectors
 */
template<class T> class Vec2d
{
	protected:
		T m_elem[2];

	public:
		Vec2d()
		{
			m_elem[0] = T(0);
			m_elem[1] = T(0);
		}

		Vec2d(const T& t0, const T& t1)
		{
			m_elem[0] = t0;
			m_elem[1] = t1;
		}

		virtual ~Vec2d()
		{}

		const Vec2d<T>& operator=(const Vec2d<T>& vec)
		{
			m_elem[0] = vec.m_elem[0];
			m_elem[1] = vec.m_elem[1];

			return *this;
		}

		Vec2d(const Vec2d<T>& vec)
		{
			operator=(vec);
		}

		T& operator[](int iIdx)
		{
			return m_elem[iIdx];
		}

		const T& operator[](int iIdx) const
		{
			return m_elem[iIdx];
		}

		T& operator()(int iIdx)
		{
			return operator[](iIdx);
		}

		const T& operator()(int iIdx) const
		{
			return operator[](iIdx);
		}

		T length() const
		{
			return sqrt(m_elem[0]*m_elem[0] + m_elem[1]*m_elem[1]);
		}

		void normalize()
		{
			T len = length();
			m_elem[0] /= len;
			m_elem[1] /= len;
		}

		template<class S> Vec2d<S> cast() const
		{
			Vec2d<S> vecRet;

			vecRet[0] = S(m_elem[0]);
			vecRet[1] = S(m_elem[1]);

			return vecRet;
		}
};

template<class T> Vec2d<T> operator+(const Vec2d<T>& vec0, const Vec2d<T>& vec1)
{
	Vec2d<T> vecRet;
	vecRet[0] = vec0[0] + vec1[0];
	vecRet[1] = vec0[1] + vec1[1];
	return vecRet;
}

template<class T> Vec2d<T> operator-(const Vec2d<T>& vec0, const Vec2d<T>& vec1)
{
	Vec2d<T> vecRet;
	vecRet[0] = vec0[0] - vec1[0];
	vecRet[1] = vec0[1] - vec1[1];
	return vecRet;
}

// scale
template<class T> Vec2d<T> operator*(const T& t, const Vec2d<T>& vec)
{
	Vec2d<T> vecRet;
	vecRet[0] = t*vec[0];
	vecRet[1] = t*vec[1];
	return vecRet;
}

template<class T> Vec2d<T> operator*(const Vec2d<T>& vec, const T& t)
{
	return operator*(t, vec);
}

// inner product
template<class T> T operator*(const Vec2d<T>& vec0, const Vec2d<T>& vec1)
{
	return vec0[0]*vec1[0] + vec0[1]*vec1[1];
}

template <class T> std::ostream& operator<<(std::ostream& ostr,
											const Vec2d<T>& vec)
{
	ostr << "(" << vec[0] << ", " << vec[1] << ")";
	return ostr;
}

#endif
