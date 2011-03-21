// Klassen, um die TOF- und PAD-Datentypen mit Qwt zu nutzen

#ifndef __TOFDATA__
#define __TOFDATA__

#include <qwt/qwt_plot_spectrogram.h>
#include "tofloader.h"

class MainRasterData : public QwtRasterData
{
	protected:
		bool m_bLog;
		
	public:
		MainRasterData(const QwtDoubleRect& rect);
		
		void SetLog10(bool bLog10);
		bool GetLog10(void) const;
		
		// Wert ohne Berücksichtigung von m_bLog nichtlogarithmisch zurückgeben
		virtual double GetValueRaw(int x, int y) const = 0;
};


// *********************** PAD-Daten *********************** 
class PadData : public MainRasterData, public PadImage
{
	protected:
	
	public:
		PadData();
		PadData(const PadData& pad);
		virtual ~PadData();

		virtual QwtRasterData *copy() const;
		virtual QwtDoubleInterval range() const;
		virtual double value(double x, double y) const;
		virtual double GetValueRaw(int x, int y) const;
};


// *********************** TOF-Daten ***********************
class Data2D : public MainRasterData, public TmpImage
{
	protected:
		bool m_bPhaseData;

	public:
		Data2D(const QwtDoubleRect& rect);
		Data2D();
		Data2D(const Data2D& data2d);
		virtual ~Data2D();
		
		void SetPhaseData(bool bPhaseData);	// wegen Achsen-Range
		void clearData();
		
		virtual QwtRasterData *copy() const;
		virtual QwtDoubleInterval range() const;
		virtual double value(double x, double y) const;
		virtual double GetValueRaw(int x, int y) const;
};

#endif
