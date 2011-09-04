%Module livewidget 0

%Import QtGui/QtGuimod.sip
%Import QtCore/QtCoremod.sip
%Import Qwt5/QwtModule.sip


class LWData : QwtRasterData
{
%TypeHeaderCode
#include "../lw_data.h"
%End
  public:
    LWData(const QwtDoubleRect& rect);
    LWData(int width, int height, int depth=1, const char *data=NULL);

    void setLog10(bool val);
    bool isLog10() const;

    // QwtRasterData overridables
    virtual QwtRasterData *copy() const;
    virtual QwtDoubleInterval range() const;
    virtual double value(double x, double y) const;

    // get raw (nonlog) value independent of m_bLog
    double valueRaw(int x, int y) const;
};

class LWPlot : QwtPlot
{
%TypeHeaderCode
#include "../lw_widget.h"
%End
  public:
    LWPlot(QWidget *parent);

    void changeRange();
    QwtPlotZoomer *getZoomer();
    QwtPlotPanner *getPanner();

    void setData(QwtRasterData *data);
    const QwtRasterData *getData() const;

  public slots:
    void printPlot();
};


class LWWidget : QWidget
{
%TypeHeaderCode
#include "../lw_widget.h"
%End
  public:
    LWWidget(QWidget *parent = NULL);
    virtual ~LWWidget();

    void setData(LWData *data);
    LWPlot *plot();

  public slots:
    void setLog10(bool bLog10);

    void updateGraph();
    void updateLabels();
};
