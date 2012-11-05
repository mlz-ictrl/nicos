CONFIG += qt staticlib
TEMPLATE = lib

FORMS += ../ui/batchdlg.ui ../ui/commanddlg.ui ../ui/gcdlg.ui ../ui/rangedlg.ui ../ui/serverdlg.ui \
	../ui/browsedlg.ui ../ui/contrastsvsimagesdlg.ui ../ui/graphdlg.ui ../ui/roidlg.ui ../ui/sumdialog.ui \
	../ui/calibrationdlg.ui ../ui/countsvsimagesdlg.ui ../ui/integrationdlg.ui ../ui/servercfgdlg.ui


INCLUDEPATH += . /usr/include/qwt /usr/include/qwt5 /usr/include/libxml2 /usr/include/qwt-qt4

HEADERS += ../loader/tofloader.h ../aux/fourier.h ../loader/padloader.h ../loader/basicimage.h \
	../config/globals.h   ../plot/tofdata.h   ../main/cascadewidget.h  ../dialogs/cascadedialogs.h \
	../plot/bins.h   ../plot/histogram_item.h ../aux/helper.h ../aux/logger.h ../aux/roi.h \
	../config/config.h ../aux/fit.h ../aux/gc.h ../plot/plotter.h ../loader/conf.h

SOURCES += ../loader/tofloader.cpp ../aux/fourier.cpp ../loader/padloader.cpp ../config/globals.cpp \
 	   ../plot/tofdata.cpp ../main/cascadewidget.cpp ../dialogs/cascadedialogs.cpp \
	../plot/bins.cpp ../plot/histogram_item.cpp ../aux/helper.cpp ../aux/logger.cpp \
	../aux/roi.cpp ../config/config.cpp ../aux/fit.cpp ../aux/gc.cpp ../plot/plotter.cpp \
	../loader/conf.cpp

LIBS += -lMinuit2 -lgomp -lQtNetwork -lqwt -lxml++-2.6
