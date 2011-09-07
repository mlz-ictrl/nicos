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

    int width() const;
    int height() const;
    int depth() const;
    double min() const;
    double max() const;

    void setLog10(bool val);
    bool isLog10() const;

    bool hasCustomRange() const;
    double customRangeMin() const;
    double customRangeMax() const;
    void setCustomRange(double lower, double upper);

    double value(double x, double y) const;
    double valueRaw(int x, int y) const;
    double valueRaw(int x, int y, int z) const;

    void histogram(int bins, QVector<double> **xs, QVector<double> **ys) const;
};

class LWPlot : QwtPlot
{
%TypeHeaderCode
#include "../lw_widget.h"
%End
  public:
    LWPlot(QWidget *parent);

    void updateRange();
    QwtPlotZoomer *getZoomer();
    QwtPlotPanner *getPanner();
    const QwtRasterData *getData() const;

    void setData(QwtRasterData *data);
    void setColorMap(QwtColorMap &map);

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

    LWData *data();
    void setData(LWData *data /Transfer/);

    void setCustomRange(double lower, double upper);
    void setStandardColorMap(bool greyscale, bool cyclic);

    LWPlot *plot();

  public slots:
    void setLog10(bool bLog10);

    void updateGraph();
    void updateLabels();
};
