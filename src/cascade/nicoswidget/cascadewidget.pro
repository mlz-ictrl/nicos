CONFIG += qt staticlib
TEMPLATE = lib

FORMS += ../calibrationdlg.ui ../graphdlg.ui ../servercfgdlg.ui ../serverdlg.ui ../sumdialog.ui
INCLUDEPATH += . /usr/include/qwt
HEADERS += ../tofloader.h   ../globals.h   ../tofdata.h   ../cascadewidget.h  ../cascadedialogs.h   ../bins.h   ../histogram_item.h ../helper.h ../logger.h ../roi.h ../config.h
SOURCES += ../tofloader.cpp ../globals.cpp ../tofdata.cpp ../cascadewidget.cpp ../cascadedialogs.cpp ../bins.cpp ../histogram_item.cpp ../helper.cpp ../logger.cpp ../roi.cpp ../config.cpp
LIBS += -lMinuit2 -lgomp -lQtNetwork -lqwt -lxml++-2.6
