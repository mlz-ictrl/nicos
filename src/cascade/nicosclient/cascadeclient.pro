CONFIG += qt staticlib
TEMPLATE = lib

HEADERS += ../client.h ../tofloader.h ../globals.h ../helper.h ../logger.h
SOURCES += ../client.cpp ../nicosclient.cpp ../tofloader.cpp ../globals.cpp ../helper.cpp ../logger.cpp
LIBS += -lQtNetwork -lMinuit2 -lgomp
