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

#ifndef __MAT2d__
#define __MAT2d__

#include <iostream>
#include "vec2d.h"

/*
 * 2D matrices
 */
template<class T> class Mat2d
{
	protected:
		// ( 00 01 )
		// ( 10 11 )
		T m_elem[2][2];

	public:
		Mat2d()
		{
			m_elem[0][0] = m_elem[0][1] = T(0);
			m_elem[1][0] = m_elem[1][1] = T(0);
		}

		Mat2d(const T& t00, const T& t01, const T& t10, const T& t11)
		{
			m_elem[0][0] = t00;
			m_elem[0][1] = t01;
			m_elem[1][0] = t10;
			m_elem[1][1] = t11;
		}

		virtual ~Mat2d()
		{}

		const Mat2d<T>& operator=(const Mat2d<T>& mat)
		{
			m_elem[0][0] = mat.m_elem[0][0];
			m_elem[0][1] = mat.m_elem[0][1];
			m_elem[1][0] = mat.m_elem[1][0];
			m_elem[1][1] = mat.m_elem[1][1];

			return *this;
		}

		Mat2d(const Mat2d<T>& mat)
		{
			operator=(mat);
		}

		T& operator()(int i, int j)
		{
			return m_elem[i][j];
		}

		const T& operator()(int i, int j) const
		{
			return m_elem[i][j];
		}

		T det() const
		{
			return m_elem[0][0]*m_elem[1][1] - m_elem[0][1]*m_elem[1][0];
		}

		// see: http://mathworld.wolfram.com/MatrixInverse.html
		Mat2d<T> inverse() const
		{
			Mat2d<T> matRet;

			T tdet_inv = T(1) / det();

			matRet(0,0) = m_elem[1][1] * tdet_inv;
			matRet(0,1) = -m_elem[0][1] * tdet_inv;
			matRet(1,0) = -m_elem[1][0] * tdet_inv;
			matRet(1,1) = m_elem[0][0] * tdet_inv;

			return matRet;
		}

		template<class S> Mat2d<S> cast() const
		{
			Mat2d<S> matRet;

			matRet(0,0) = S(m_elem[0][0]);
			matRet(0,1) = S(m_elem[0][1]);
			matRet(1,0) = S(m_elem[1][0]);
			matRet(1,1) = S(m_elem[1][1]);

			return matRet;
		}

		static const Mat2d<T>& unity()
		{
			static const Mat2d<T> matunity(1,0,0,1);
			return matunity;
		}

		static const Mat2d<T>& zero()
		{
			static const Mat2d<T> matzero(0,0,0,0);
			return matzero;
		}

		static Mat2d<T> rotation(T tangle)
		{
			Mat2d<T> matrot;

			const T tc = cos(tangle);
			const T ts = sin(tangle);

			matrot(0,0) = tc;
			matrot(0,1) = -ts;
			matrot(1,0) = ts;
			matrot(1,1) = tc;

			return matrot;
		}
};

template<class T> Mat2d<T> operator+(const Mat2d<T>& mat0, const Mat2d<T>& mat1)
{
	Mat2d<T> matRet;
	matRet(0,0) = mat0(0,0) + mat1(0,0);
	matRet(0,1) = mat0(0,1) + mat1(0,1);
	matRet(1,0) = mat0(1,0) + mat1(1,0);
	matRet(1,1) = mat0(1,1) + mat1(1,1);
	return matRet;
}

template<class T> Mat2d<T> operator-(const Mat2d<T>& mat0, const Mat2d<T>& mat1)
{
	Mat2d<T> matRet;
	matRet(0,0) = mat0(0,0) - mat1(0,0);
	matRet(0,1) = mat0(0,1) - mat1(0,1);
	matRet(1,0) = mat0(1,0) - mat1(1,0);
	matRet(1,1) = mat0(1,1) - mat1(1,1);
	return matRet;
}

// scale
template<class T> Mat2d<T> operator*(const T& t, const Mat2d<T>& mat)
{
	Mat2d<T> matRet;
	matRet(0,0) *= t;
	matRet(0,1) *= t;
	matRet(1,0) *= t;
	matRet(1,1) *= t;
	return matRet;
}

// matrix multiplication
template<class T> Mat2d<T> operator*(const Mat2d<T>& mat0, const Mat2d<T>& mat1)
{
	Mat2d<T> matRet;

	matRet(0,0) = mat0(0,0)*mat1(0,0) + mat0(0,1)*mat1(1,0);
	matRet(0,1) = mat0(0,0)*mat1(0,1) + mat0(0,1)*mat1(1,1);
	matRet(1,0) = mat0(1,0)*mat1(0,0) + mat0(1,1)*mat1(1,0);
	matRet(1,1) = mat0(1,0)*mat1(0,1) + mat0(1,1)*mat1(1,1);

	return matRet;
}

// matrix vector multiplication
template<class T> Vec2d<T> operator*(const Mat2d<T>& mat, const Vec2d<T>& vec)
{
	Vec2d<T> vecRet;

	vecRet[0] = mat(0,0)*vec[0] + mat(0,1)*vec[1];
	vecRet[1] = mat(1,0)*vec[0] + mat(1,1)*vec[1];

	return vecRet;
}

template<class T> Mat2d<T> operator*(const Mat2d<T>& mat, const T& t)
{
	return operator*(t, mat);
}

template <class T> std::ostream& operator<<(std::ostream& ostr,
											const Mat2d<T>& mat)
{
	ostr << "(" << mat(0,0) << ", " << mat(0,1) << "; "
				<< mat(1,0) << ", " << mat(1,1) << ")";
	return ostr;
}

#endif
