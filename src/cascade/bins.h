// Werte in Bins einordnen

class Bins
{
	protected:
		QwtArray<QwtDoubleInterval> m_intervals;
		QwtArray<double> m_values;
		
		int m_iNumBins;
		double m_dMin, m_dMax, m_dInterval;
		
	public:
		Bins(int iNumBins, double dMin, double dMax) : m_iNumBins(iNumBins), m_dMin(dMin), m_dMax(dMax), m_intervals(iNumBins), m_values(iNumBins)
		{
			m_dInterval = (dMax-dMin)/double(iNumBins);
			
			for(int i=0; i<iNumBins; ++i)
			{
				m_intervals[i] = QwtDoubleInterval(dMin + double(i)*m_dInterval, dMin + (double(i)+1.)*m_dInterval);
			}
		}
		
		// Zähler des Bins, in dem dWert liegt, erhöhen
		void Inc(double dWert)
		{	
			if(dWert!=dWert) return; // NaN ignorieren

			int iBin = int((dWert-m_dMin) / m_dInterval);
			if(iBin<0 || iBin>m_iNumBins) return;
			
			m_values[iBin] += 1.;
		}
		
		double GetMaxVal() const
		{
			double dMax=0.;
			for(int i=0; i<m_iNumBins; ++i)
			{
				if(m_values[i]>dMax) dMax=m_values[i];
			}
			return dMax;
		}
		
		// in Qwt-kompatibles Format umwandeln
		const QwtArray<QwtDoubleInterval>& GetIntervals() const { return m_intervals; }
		const QwtArray<double>& GetValues() const { return m_values; }
};
