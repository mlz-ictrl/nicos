CONFIG += qt debug

INCLUDEPATH += . /usr/include/qwt5 /usr/include/qwt-qt4 /usr/include/qwt /usr/include/cfitsio /usr/include/cfitsio0

LIBS += -lqwt-qt4 -lcfitsio

TARGET = livewidget

HEADERS += \
    lw_common.h \
    lw_widget.h \
    lw_plot.h \
    lw_controls.h \
    lw_histogram.h \
    lw_data.h \
    lw_profile.h \
    lw_imageproc.h

SOURCES += \
    lw_widget.cpp \
    lw_plot.cpp \
    lw_controls.cpp \
    lw_histogram.cpp \
    lw_data.cpp \
    lw_profile.cpp \
    lw_main.cpp \
    lw_imageproc.cpp
