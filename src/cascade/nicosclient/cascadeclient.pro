CONFIG += qt staticlib
TEMPLATE = lib

HEADERS += ../client.h ../tofloader.h ../helper.h ../logger.h
SOURCES += ../client.cpp ../nicosclient.cpp ../tofloader.cpp ../helper.cpp ../logger.cpp
LIBS += -lQtNetwork -lMinuit2 -lgomp
