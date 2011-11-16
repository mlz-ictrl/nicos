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


#ifndef __CASCADE_FITTER__
#define __CASCADE_FITTER__

bool FitSinus(int iSize, const unsigned int* pData,
			  double &dPhase, /*double &dScale,*/
			  double &dAmp, double &dOffs);


bool FitGaussian(int iSizeX, int iSizeY,
				 const unsigned int* pData,
				 double &dAmp,
				 double &dCenterX, double &dCenterY,
				 double &dSpreadX, double &dSpreadY);

#endif
