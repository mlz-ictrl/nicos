#
# Makefile for Cascade Viewer
# (and Cascade Nicos Modules)
#
# * "make".................build all
# * "make cascade".........build Cascade Viewer
# * "make nicosmodules"....build Nicos Modules
#
# * "make clean"...........clean all
# * "make clean_qt"........clean Cascade Viewer
# * "make clean_nicos".....clean Nicos Modules
# *
#


COMPILER	= gcc
FLAGS		= -O2 -march=native -Wall -Wextra -D __CASCADE_QT_CLIENT__ -DNDEBUG

LIBS		= -lQtCore -lQtGui -lQtNetwork -lMinuit2 -lgomp -lxml2 \
		   -lstdc++ -lm -lfftw3 -lqwt-qt4 \
		   -L /usr/lib/qt4

INCLUDES	= -I /usr/include/qwt -I /usr/include/qwt5 -I /usr/include/qt4 \
                  -I /usr/include/Qt -I /usr/include/QtCore -I /usr/include/QtGui \
                  -I /usr/include/qt4/Qt -I /usr/include/qt4/QtCore -I /usr/include/qt4/QtGui \
                  -I /usr/include/libxml2 -I /usr/include/qwt-qt4


all: cascade nicosmodules



###################### cascade-qt-client ################
cascade: cascade.o cascadedialogs.o bins.o cascadewidget.o tofloader.o tofdata.o \
	 config.o xml.o histogram_item.o client.o helper.o logger.o globals.o parse.o \
	roi.o fit.o gc.o plotter.o padloader.o fourier.o casc_conf.o
	$(COMPILER) $(FLAGS) -o cascade cascade.o cascadedialogs.o \
		bins.o cascadewidget.o tofloader.o tofdata.o config.o \
		xml.o casc_conf.o \
		histogram_item.o client.o helper.o logger.o globals.o \
		parse.o roi.o fit.o gc.o plotter.o padloader.o fourier.o \
		${LIBS}
#########################################################




###################### CPP-Dateien ######################
cascade.o: main/cascade.cpp main/cascade.moc dialogs/cascadedialogs_moc.cpp dialogs/cascadedialogs.moc \
		plot/bins.h aux/parse.h plot/ErrorBarPlotCurve.h plot/tofdata.h dialogs/cascadedialogs.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o cascade.o main/cascade.cpp

cascadedialogs.o: dialogs/cascadedialogs_moc.cpp dialogs/cascadedialogs.h dialogs/cascadedialogs.moc \
	dialogs/cascadedialogs_tof.cpp dialogs/cascadedialogs_pad.cpp dialogs/cascadedialogs_server.cpp
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o cascadedialogs.o dialogs/cascadedialogs_moc.cpp

bins.o: plot/bins.cpp plot/bins.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o bins.o plot/bins.cpp

cascadewidget.o: main/cascadewidget_moc.cpp main/cascadewidget.h main/cascadewidget.moc
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o cascadewidget.o main/cascadewidget_moc.cpp

plotter.o: plot/plotter_moc.cpp plot/plotter.cpp plot/plotter.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o plotter.o plot/plotter_moc.cpp

tofloader.o: loader/tofloader.cpp loader/tofloader.h loader/tofloader_image.cpp loader/tofloader_graph.cpp
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o tofloader.o loader/tofloader.cpp

padloader.o: loader/padloader.cpp loader/padloader.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o padloader.o loader/padloader.cpp

tofdata.o: plot/tofdata.cpp plot/tofdata.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o tofdata.o plot/tofdata.cpp

fourier.o: aux/fourier.cpp aux/fourier.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o fourier.o aux/fourier.cpp

config.o: config/config.cpp config/config.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o config.o config/config.cpp

casc_conf.o: loader/conf.cpp loader/conf.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o casc_conf.o loader/conf.cpp

xml.o: aux/xml.cpp aux/xml.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o xml.o aux/xml.cpp

histogram_item.o: plot/histogram_item.cpp plot/histogram_item.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o histogram_item.o plot/histogram_item.cpp

client.o: client/client_moc.cpp client/client.h client/client.moc
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o client.o client/client_moc.cpp

helper.o: aux/helper.cpp aux/helper.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o helper.o aux/helper.cpp

logger.o: aux/logger.cpp aux/logger.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o logger.o aux/logger.cpp

globals.o: config/globals.cpp config/globals.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o globals.o config/globals.cpp

parse.o: aux/parse.cpp aux/parse.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o parse.o aux/parse.cpp

roi.o: aux/roi.cpp aux/roi.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o roi.o aux/roi.cpp

fit.o: aux/fit.cpp aux/fit.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o fit.o aux/fit.cpp

gc.o: aux/gc.cpp aux/gc.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o gc.o aux/gc.cpp
#########################################################



############################ Dialogs ############################
dialogs/cascadedialogs.h: ui/ui_calibrationdlg.h ui/ui_sumdialog.h \
		  ui/ui_serverdlg.h \
		  ui/ui_servercfgdlg.h ui/ui_graphdlg.h ui/ui_commanddlg.h \
		  ui/ui_roidlg.h ui/ui_browsedlg.h ui/ui_integrationdlg.h \
		  ui/ui_rangedlg.h ui/ui_countsvsimagesdlg.h \
		  ui/ui_contrastsvsimagesdlg.h ui/ui_batchdlg.h \
		  ui/ui_gcdlg.h

ui/ui_calibrationdlg.h: ui/calibrationdlg.ui
	uic ui/calibrationdlg.ui > ui/ui_calibrationdlg.h

ui/ui_sumdialog.h: ui/sumdialog.ui
	uic ui/sumdialog.ui > ui/ui_sumdialog.h

ui/ui_serverdlg.h: ui/serverdlg.ui
	uic ui/serverdlg.ui > ui/ui_serverdlg.h

ui/ui_servercfgdlg.h: ui/servercfgdlg.ui
	uic ui/servercfgdlg.ui > ui/ui_servercfgdlg.h

ui/ui_graphdlg.h: ui/graphdlg.ui
	uic ui/graphdlg.ui > ui/ui_graphdlg.h

ui/ui_commanddlg.h: ui/commanddlg.ui
	uic ui/commanddlg.ui > ui/ui_commanddlg.h

ui/ui_roidlg.h: ui/roidlg.ui
	uic ui/roidlg.ui > ui/ui_roidlg.h

ui/ui_browsedlg.h: ui/browsedlg.ui
	uic ui/browsedlg.ui > ui/ui_browsedlg.h

ui/ui_integrationdlg.h: ui/integrationdlg.ui
	uic ui/integrationdlg.ui > ui/ui_integrationdlg.h

ui/ui_rangedlg.h: ui/rangedlg.ui
	uic ui/rangedlg.ui > ui/ui_rangedlg.h

ui/ui_countsvsimagesdlg.h: ui/countsvsimagesdlg.ui
	uic ui/countsvsimagesdlg.ui > ui/ui_countsvsimagesdlg.h

ui/ui_contrastsvsimagesdlg.h: ui/contrastsvsimagesdlg.ui
	uic ui/contrastsvsimagesdlg.ui > ui/ui_contrastsvsimagesdlg.h

ui/ui_batchdlg.h: ui/batchdlg.ui
	uic ui/batchdlg.ui > ui/ui_batchdlg.h

ui/ui_gcdlg.h: ui/gcdlg.ui
	uic ui/gcdlg.ui > ui/ui_gcdlg.h
#################################################################



###################### MOC-Dateien ######################
main/cascade.moc:
	moc main/cascade.cpp -o main/cascade.moc


main/cascadewidget_moc.cpp: main/cascadewidget.cpp main/cascadewidget.moc
	cat main/cascadewidget.cpp main/cascadewidget.moc > main/cascadewidget_moc.cpp

main/cascadewidget.moc:
	moc main/cascadewidget.h -o main/cascadewidget.moc


plot/plotter_moc.cpp: plot/plotter.cpp plot/plotter.moc
	cat plot/plotter.cpp plot/plotter.moc > plot/plotter_moc.cpp

plot/plotter.moc:
	moc plot/plotter.h -o plot/plotter.moc


dialogs/cascadedialogs_moc.cpp: dialogs/cascadedialogs.cpp dialogs/cascadedialogs.moc
	cat dialogs/cascadedialogs.cpp dialogs/cascadedialogs.moc > dialogs/cascadedialogs_moc.cpp

dialogs/cascadedialogs.moc:
	moc dialogs/cascadedialogs.h -o dialogs/cascadedialogs.moc


client/client_moc.cpp: client/client.cpp client/client.moc
	cat client/client.cpp client/client.moc > client/client_moc.cpp

client/client.moc:
	moc client/client.h -o client/client.moc
#########################################################




###################### clean ######################
# Qt-Client
clean_qt:
	rm -f *.moc *_moc.cpp
	rm -f client/*.moc client/*_moc.cpp
	rm -f dialogs/*.moc dialogs/*_moc.cpp
	rm -f main/*.moc main/*_moc.cpp
	rm -f plot/*.moc plot/*_moc.cpp

	rm -f ui_*.h
	rm -f ui/ui_*.h

	rm -f *~ aux/*~ client/*~ config/*~ dialogs/*~ loader/*~ main/*~ plot/*~ ui/*~
	rm -f *.o
	rm -f cascade

# Nicos-Module
clean_nicos:
	rm -f nicosclient/Makefile
	rm -f nicosclient/*.a nicosclient/pythonbinding/*.so
	rm -f nicosclient/*.o nicosclient/pythonbinding/*.o
	rm -f nicosclient/moc_*
	rm -f nicosclient/pythonbinding/Makefile
	rm -f nicosclient/pythonbinding/sip*.cpp nicosclient/pythonbinding/sip*.h
	rm -f nicosclient/pythonbinding/*.exp nicosclient/pythonbinding/*.sbf

	rm -f nicoswidget/Makefile
	rm -f nicoswidget/*.a nicoswidget/pythonbinding/*.so
	rm -f nicoswidget/*.o nicoswidget/pythonbinding/*.o
	rm -f nicoswidget/moc_*
	rm -f nicoswidget/ui_*.h
	rm -f nicoswidget/pythonbinding/Makefile
	rm -f nicoswidget/pythonbinding/sip*.cpp nicoswidget/pythonbinding/sip*.h
	rm -f nicoswidget/pythonbinding/*.exp nicoswidget/pythonbinding/*.sbf

clean: clean_qt clean_nicos
###################################################




#################### NICOS-Libraries #####################
nicosmodules: nicosclient/pythonbinding/cascadeclient.so nicoswidget/pythonbinding/cascadewidget.so

nicosmodules-client: nicosclient/pythonbinding/cascadeclient.so

nicosmodules-widget: nicoswidget/pythonbinding/cascadewidget.so

nicosclient/libcascadeclient.a:
	cd nicosclient && qmake && make

nicosclient/pythonbinding/cascadeclient.so: nicosclient/pythonbinding/cascadeclient.sip nicosclient/libcascadeclient.a
	cd nicosclient/pythonbinding && python configure.py && make

nicoswidget/libcascadewidget.a:
	-cd nicoswidget && qmake && make

nicoswidget/pythonbinding/cascadewidget.so: nicoswidget/pythonbinding/cascadewidget.sip nicoswidget/libcascadewidget.a
	-cd nicoswidget/pythonbinding && python configure.py && make
##########################################################
