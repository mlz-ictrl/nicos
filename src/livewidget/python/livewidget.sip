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

    int currentZ() const;
    virtual void setCurrentZ(int val);

    bool isLog10() const;
    virtual void setLog10(bool val);

    bool hasCustomRange() const;
    double customRangeMin() const;
    double customRangeMax() const;
    virtual void setCustomRange(double lower, double upper);

    virtual double value(double x, double y) const;
    virtual double valueRaw(int x, int y) const;
    virtual double valueRaw(int x, int y, int z) const;

    virtual void histogram(int bins, QVector<double> **xs,
                           QVector<double> **ys) const;
};


class LWZoomer : QwtPlotZoomer
{
%TypeHeaderCode
#include "../lw_widget.h"
%End
  public:
    LWZoomer(QwtPlotCanvas *canvas, const QwtPlotSpectrogram *spectro);
};


class LWPlot : QwtPlot
{
%TypeHeaderCode
#include "../lw_plot.h"
%End
  public:
    LWPlot(QWidget *parent);

    void updateRange();
    LWZoomer *getZoomer();
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

    LWPlot *plot();

    LWData *data();
    void setData(LWData *data /Transfer/);

    bool isLog10() const;
    bool keepAspect() const;
    bool controlsVisible() const;

    void setCustomRange(double lower, double upper);
    void setStandardColorMap(bool greyscale, bool cyclic);

  public slots:
    void setLog10(bool val);
    void setKeepAspect(bool val);
    void setControlsVisible(bool val);

    void updateGraph();
    void updateLabels();

  signals:
    void dataUpdated(LWData *data);
};
