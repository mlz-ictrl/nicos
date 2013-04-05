CONFIG += qt debug
#TEMPLATE = lib

INCLUDEPATH += . /usr/include/qwt5 /usr/include/qwt-qt4
LIBS += -lqwt-qt4

HEADERS += \
    lw_widget.h \
    lw_plot.h \
    lw_controls.h \
    lw_histogram.h \
    lw_data.h \
    lw_profile.h
SOURCES += \
    lw_widget.cpp \
    lw_plot.cpp \
    lw_controls.cpp \
    lw_histogram.cpp \
    lw_data.cpp \
    lw_profile.cpp \
    lw_main.cpp
