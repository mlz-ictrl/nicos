%Module livewidget 0

%Import QtGui/QtGuimod.sip
%Import QtCore/QtCoremod.sip
%Import Qwt5/QwtModule.sip


class LWData
{
%TypeHeaderCode
#include "../lw_data.h"
%End
  public:
    LWData(const LWData &other);
    LWData(int width, int height, int depth, const char *data);
    LWData(int width, int height, int depth,
           const char *format, const char *data);

    void setLog10(bool val);
    bool isLog10() const;

    bool hasCustomRange() const;
    double customRangeMin() const;
    double customRangeMax() const;
    void setCustomRange(double lower, double upper);

    double value(double x, double y) const;
    double valueRaw(int x, int y) const;
    double valueRaw(int x, int y, int z) const;
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

    void setData(LWData *data /Transfer/);
    LWPlot *plot();

  public slots:
    void setLog10(bool bLog10);

    void updateGraph();
    void updateLabels();
};
