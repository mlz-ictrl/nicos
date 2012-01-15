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

/*
 * drawing of error bars
 * based on the following python code:
 * http://pyqwt.sourceforge.net/examples/ErrorBarDemo.py.html
 */
#ifndef __ERROR_BARS__
#define __ERROR_BARS__

class ErrorBarPlotCurve : public QwtPlotCurve
{
	protected:
		QPen m_errorPen;
		int m_errorCap;

		double *m_pddy;		// Fehler in y-Richtung
		int m_iLen;

		void Clear()
		{
			if(m_pddy) { delete[] m_pddy; m_pddy=NULL; }
			m_iLen=0;
		}

	public:
		ErrorBarPlotCurve(const char* pcName) : QwtPlotCurve(pcName),
												m_pddy(NULL), m_iLen(0)
		{
			//setPen(QPen(QColor(Qt::black), 1));
			//setStyle(QwtPlotCurve::Lines);
			//setSymbol(QwtSymbol(QwtSymbol::Ellipse, QBrush(QColor(Qt::red)),
			//					  QPen(QColor(Qt::black), 1), QSize(4, 4)));
			m_errorPen = QPen(QColor(Qt::blue), 1);
			m_errorCap = 5;
		}

		virtual ~ErrorBarPlotCurve()
		{
			Clear();
		}

		virtual void setData(const double *pdx, const double *pdy, int iLen)
		{
			Clear();
			QwtPlotCurve::setData(pdx, pdy, iLen);

			m_iLen=iLen;
			m_pddy = new double[iLen];

			for(int i=0; i<iLen; ++i)
				m_pddy[i] = sqrt(pdy[i]);
		}

		virtual void draw(QPainter *painter, const QwtScaleMap& xMap,
						const QwtScaleMap& yMap, int first, int last = -1) const
		{
			if(last<0) last = m_iLen-1;
			QwtPlotCurve::draw(painter, xMap, yMap, first, last);

			painter->save();
			painter->setPen(m_errorPen);

			const QwtData& data = QwtPlotCurve::data();
			if(m_pddy)
			{
				double *ymin = new double[m_iLen];
				double *ymax = new double[m_iLen];

				QLine *pLines = new QLine[m_iLen];
				for(int i=0; i<m_iLen; ++i)
				{
					ymin[i] = (data.y(i) - m_pddy[i]);
					ymax[i] = (data.y(i) + m_pddy[i]);

					int xi = xMap.transform(data.x(i));
					pLines[i] = QLine(QLine(xi, yMap.transform(ymin[i]),xi,
											yMap.transform(ymax[i])));
				}
				painter->drawLines(pLines, m_iLen);
				delete[] pLines;

				pLines = new QLine[m_iLen*2];
				if(m_errorCap>0)
				{
					int cap = m_errorCap/2;
					for(int i=0; i<m_iLen; ++i)
					{
						int xi = xMap.transform(data.x(i));
						pLines[i*2] = QLine(xi-cap, yMap.transform(ymin[i]),
											xi+cap, yMap.transform(ymin[i]));
						pLines[i*2+1] = QLine(xi-cap, yMap.transform(ymax[i]),
											  xi+cap, yMap.transform(ymax[i]));
					}
					painter->drawLines(pLines, m_iLen*2);
				}
				delete[] pLines;
				delete[] ymin;
				delete[] ymax;
			}
			painter->restore();
		}
};
#endif
