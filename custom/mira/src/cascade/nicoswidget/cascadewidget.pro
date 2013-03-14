CONFIG += qt staticlib
TEMPLATE = lib

FORMS += ../ui/batchdlg.ui ../ui/commanddlg.ui ../ui/gcdlg.ui ../ui/rangedlg.ui ../ui/serverdlg.ui \
	../ui/browsedlg.ui ../ui/contrastsvsimagesdlg.ui ../ui/graphdlg.ui ../ui/roidlg.ui ../ui/sumdialog.ui \
	../ui/calibrationdlg.ui ../ui/countsvsimagesdlg.ui ../ui/integrationdlg.ui ../ui/servercfgdlg.ui


INCLUDEPATH += . /usr/include/qwt /usr/include/qwt5 /usr/include/libxml2 /usr/include/qwt-qt4

HEADERS += ../loader/tofloader.h ../auxiliary/fourier.h ../loader/padloader.h ../loader/basicimage.h \
	../config/globals.h   ../plot/tofdata.h   ../main/cascadewidget.h  ../dialogs/cascadedialogs.h \
	../plot/bins.h   ../plot/histogram_item.h ../auxiliary/helper.h ../auxiliary/logger.h ../auxiliary/roi.h \
	../config/config.h ../auxiliary/fit.h ../auxiliary/gc.h ../plot/plotter.h ../loader/conf.h

SOURCES += ../loader/tofloader.cpp ../auxiliary/fourier.cpp ../loader/padloader.cpp ../config/globals.cpp \
 	   ../plot/tofdata.cpp ../main/cascadewidget.cpp ../dialogs/cascadedialogs.cpp \
	../plot/bins.cpp ../plot/histogram_item.cpp ../auxiliary/helper.cpp ../auxiliary/logger.cpp \
	../auxiliary/roi.cpp ../config/config.cpp ../auxiliary/fit.cpp ../auxiliary/gc.cpp ../plot/plotter.cpp \
	../loader/conf.cpp

LIBS += -lMinuit2 -lgomp -lQtNetwork -lqwt -lxml++-2.6
