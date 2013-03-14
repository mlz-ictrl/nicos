CONFIG += qt staticlib
TEMPLATE = lib

HEADERS += ../client/client.h ../loader/tofloader.h ../auxiliary/fourier.h ../loader/padloader.h ../loader/basicimage.h ../config/globals.h ../auxiliary/helper.h ../auxiliary/logger.h ../auxiliary/roi.h ../config/config.h ../auxiliary/fit.h ../auxiliary/gc.h ../loader/conf.h
SOURCES += ../client/client.cpp ../client/nicosclient.cpp ../loader/tofloader.cpp ../auxiliary/fourier.cpp ../loader/padloader.cpp ../config/globals.cpp ../auxiliary/helper.cpp ../auxiliary/logger.cpp ../auxiliary/roi.cpp ../config/config.cpp ../auxiliary/fit.cpp ../auxiliary/gc.cpp ../loader/conf.cpp
LIBS += -lQtNetwork -lMinuit2 -lgomp -lxml++-2.6
INCLUDEPATH += /usr/include/libxml2
