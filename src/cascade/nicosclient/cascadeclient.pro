CONFIG += qt staticlib
TEMPLATE = lib

HEADERS += ../client.h
SOURCES += ../client.cpp ../nicosclient.cpp
LIBS += -lQtNetwork 
