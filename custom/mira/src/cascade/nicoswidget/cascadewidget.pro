CONFIG += qt staticlib
TEMPLATE = lib

FORMS += ../calibrationdlg.ui ../graphdlg.ui ../servercfgdlg.ui ../serverdlg.ui ../sumdialog.ui
INCLUDEPATH += . /usr/include/qwt /usr/include/qwt5 /usr/include/libxml2
HEADERS += ../tofloader.h ../fourier.h ../padloader.h ../basicimage.h   ../globals.h   ../tofdata.h   ../cascadewidget.h  ../cascadedialogs.h   ../bins.h   ../histogram_item.h ../helper.h ../logger.h ../roi.h ../config.h ../fit.h ../gc.h ../plotter.h
SOURCES += ../tofloader.cpp ../fourier.cpp ../padloader.cpp ../globals.cpp ../tofdata.cpp ../cascadewidget.cpp ../cascadedialogs.cpp ../bins.cpp ../histogram_item.cpp ../helper.cpp ../logger.cpp ../roi.cpp ../config.cpp ../fit.cpp ../gc.cpp ../plotter.cpp
LIBS += -lMinuit2 -lgomp -lQtNetwork -lqwt -lxml++-2.6
