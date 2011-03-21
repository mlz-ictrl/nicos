// Zeichnen von Fehlerbalken
// basiert auf folgendem Python-Programm:
// http://pyqwt.sourceforge.net/examples/ErrorBarDemo.py.html

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
		ErrorBarPlotCurve(const char* pcName) : QwtPlotCurve(pcName), m_pddy(NULL), m_iLen(0)
		{
			//setPen(QPen(QColor(Qt::black), 1));
			//setStyle(QwtPlotCurve::Lines);
			//setSymbol(QwtSymbol(QwtSymbol::Ellipse, QBrush(QColor(Qt::red)), QPen(QColor(Qt::black), 1), QSize(4, 4)));
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
		
		virtual void draw(QPainter *painter, const QwtScaleMap& xMap, const QwtScaleMap& yMap, int first, int last = -1) const
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
					pLines[i] = QLine(QLine(xi, yMap.transform(ymin[i]),xi, yMap.transform(ymax[i])));
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
						pLines[i*2] = QLine(xi-cap, yMap.transform(ymin[i]),xi+cap, yMap.transform(ymin[i]));
						pLines[i*2+1] = QLine(xi-cap, yMap.transform(ymax[i]),xi+cap, yMap.transform(ymax[i]));
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
