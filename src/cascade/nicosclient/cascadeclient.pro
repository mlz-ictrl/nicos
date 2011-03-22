CONFIG += qt staticlib
TEMPLATE = lib

HEADERS += ../client.h ../tofloader.h
SOURCES += ../client.cpp ../nicosclient.cpp ../tofloader.cpp
LIBS += -lMinuit2 -lgomp -lQtNetwork 
