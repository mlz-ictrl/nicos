CONFIG += qt staticlib
TEMPLATE = lib

HEADERS += ../client/client.h ../loader/tofloader.h ../aux/fourier.h ../loader/padloader.h ../loader/basicimage.h ../config/globals.h ../aux/helper.h ../aux/logger.h ../aux/roi.h ../config/config.h ../aux/fit.h ../aux/gc.h
SOURCES += ../client/client.cpp ../client/nicosclient.cpp ../loader/tofloader.cpp ../aux/fourier.cpp ../loader/padloader.cpp ../config/globals.cpp ../aux/helper.cpp ../aux/logger.cpp ../aux/roi.cpp ../config/config.cpp ../aux/fit.cpp ../aux/gc.cpp
LIBS += -lQtNetwork -lMinuit2 -lgomp -lxml++-2.6
INCLUDEPATH += /usr/include/libxml2
