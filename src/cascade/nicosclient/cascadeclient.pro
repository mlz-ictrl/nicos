CONFIG += qt staticlib
TEMPLATE = lib

HEADERS += ../client.h ../tofloader.h ../helper.h
SOURCES += ../client.cpp ../nicosclient.cpp ../tofloader.cpp ../helper.cpp
LIBS += -lQtNetwork -lMinuit2 -lgomp
