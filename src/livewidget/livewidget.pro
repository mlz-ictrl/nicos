CONFIG += qt debug
# TEMPLATE = lib

INCLUDEPATH += . /usr/include/qwt5
LIBS += -lqwt -lcfitsio

HEADERS += \
    lw_widget.h \
    lw_plot.h \
    lw_controls.h \
    lw_histogram.h \
    lw_data.h
SOURCES += \
    lw_widget.cpp \
    lw_plot.cpp \
    lw_controls.cpp \
    lw_histogram.cpp \
    lw_data.cpp
