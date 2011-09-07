CONFIG += qt debug
TEMPLATE = lib

INCLUDEPATH += . /usr/include/qwt5
LIBS += -lqwt -lcfitsio

HEADERS += \
    lw_widget.h \
    lw_data.h
SOURCES += \
    lw_widget.cpp \
    lw_data.cpp
