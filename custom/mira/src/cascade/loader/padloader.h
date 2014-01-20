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
// Klassen zum Laden und Verarbeiten von Pad-Dateien

#ifndef __PADLOADER__
#define __PADLOADER__

#include "../config/globals.h"
#include "basicimage.h"
#include "../auxiliary/roi.h"
#include "tofloader.h"
#include "conf.h"

class TmpImage;

/**
 * \brief container representing a PAD image
 * 
 * corresponds to the "IMAGE" measurement type in the server & HardwareLib
 */
class PadImage : public BasicImage, public Countable
{
	friend class TmpImage;

	protected:
		/// actual data
		unsigned int *m_puiDaten;

		/// lower & upper bound values
		int m_iMin, m_iMax;

		/// PAD data stored in external memory which needs no management,
		/// i.e. allocation & freeing?
		bool m_bExternalMem;

		PadConfig m_config;

		Roi m_roi;
		bool m_bUseRoi;

		bool m_bOk;

		CascConf m_cascconf;

		/// clean up
		void Clear(void);

	public:
		/// create PAD from file (or empty PAD otherwise)
		PadImage(const char *pcFileName=NULL, bool bExternalMem=false,
				 const PadConfig* conf=0);

		/// create PAD from other PAD
		PadImage(const PadImage& pad);

		virtual ~PadImage();

		virtual int GetWidth() const;
		virtual int GetHeight() const;

		/// set pointer to external memory (if bExternalMem==true)
		void SetExternalMem(void* pvDaten);

		/// size (in ints) of PAD image
		int GetPadSize() const;

		int LoadFile(const char *pcFileName);
		int LoadTextFile(const char* pcFileName);
		int SaveFile(const char *pcFileName);

		/// load PAD from memory
		/// \param strBufLen: # of bytes
		int LoadMem(const char *strBuf, unsigned int strBufLen);

		/// calculate lower & upper bound values
		void UpdateRange();

		virtual int GetIntMin() const;
		virtual int GetIntMax() const;
		virtual double GetDoubleMin() const;
		virtual double GetDoubleMax() const;

		/// print PAD as text
		void Print(const char* pcOutFile=NULL);

		/// get specific point
		virtual unsigned int GetData(int iX, int iY) const;
		virtual double GetDoubleData(int iX, int iY) const;
		virtual unsigned int GetIntData(int iX, int iY) const;

		/// set count
		void SetData(int iX, int iY, unsigned int uiCnt);

		/// same as above, but return 0 if outside ROI (if ROI is used)
		unsigned int GetDataInsideROI(int iX, int iY,
										double *dArea=0) const;
		unsigned int GetDataOutsideROI(int iX, int iY,
										double *dArea=0) const;

		/// get pointer to internal memory
		unsigned int* GetRawData(void);

		/// total number of counts (inside ROI, if used)
		virtual unsigned int GetCounts() const;
		virtual unsigned int GetCountsSubtractBackground() const;

		/// old style GetCounts, ignoring main roi
		unsigned int GetCounts(int iStartX, int iEndX,
							   int iStartY, int iEndY) const;

		const PadConfig& GetPadConfig() const;
		const CascConf& GetLocalConfig() const;

		virtual Roi& GetRoi();
		virtual void UseRoi(bool bUseRoi=true);
		virtual bool GetUseRoi() const;

		/// filter out everything except selected regions
		TmpImage GetRoiImage() const;

		void GenerateRandomData();

		bool IsOk() const;
		
		bool SaveAsDat(const char* pcDat) const;
};

#endif
