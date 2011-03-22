CONFIG += qt staticlib
TEMPLATE = lib

HEADERS += ../tofloader.h   ../tofdata.h   ../config.h   ../cascadewidget.h   ../bins.h
SOURCES += ../tofloader.cpp ../tofdata.cpp ../config.cpp ../cascadewidget.cpp 
LIBS += -lMinuit2 -lgomp -lQtNetwork -lqwt -lxml++-2.6
