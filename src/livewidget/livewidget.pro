CONFIG += qt
#TEMPLATE = lib

INCLUDEPATH += . /usr/include/qwt5
LIBS += -lqwt

HEADERS += \
    lw_app.h \
    lw_widget.h \
    lw_data.h
SOURCES += \
    lw_app.cpp \
    lw_widget.cpp \
    lw_data.cpp
