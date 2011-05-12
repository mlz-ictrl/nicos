CONFIG += qt staticlib
TEMPLATE = lib

FORMS += ../calibrationdlg.ui ../graphdlg.ui ../servercfgdlg.ui ../serverdlg.ui ../sumdialog.ui
INCLUDEPATH += . /usr/include/qwt
HEADERS += ../tofloader.h   ../tofdata.h   ../cascadewidget.h   ../cascadedialogs.h   ../bins.h   ../histogram_item.h ../helper.h
SOURCES += ../tofloader.cpp ../tofdata.cpp ../cascadewidget.cpp ../cascadedialogs.cpp ../bins.cpp ../histogram_item.cpp ../helper.cpp
LIBS += -lMinuit2 -lgomp -lQtNetwork -lqwt
