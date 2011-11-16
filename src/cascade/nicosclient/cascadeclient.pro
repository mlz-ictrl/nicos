CONFIG += qt staticlib
TEMPLATE = lib

HEADERS += ../client.h ../tofloader.h ../globals.h ../helper.h ../logger.h ../roi.h ../config.h ../fit.h
SOURCES += ../client.cpp ../nicosclient.cpp ../tofloader.cpp ../globals.cpp ../helper.cpp ../logger.cpp ../roi.cpp ../config.cpp ../fit.cpp
LIBS += -lQtNetwork -lMinuit2 -lgomp -lxml++-2.6
INCLUDEPATH += /usr/include/libxml2
