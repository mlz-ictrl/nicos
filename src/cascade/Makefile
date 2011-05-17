#
# Makefile für den Cascade-Qt-Client und die Nicos-Module
#

COMPILER	= gcc
FLAGS		= -O2 -D __CASCADE_QT_CLIENT__
LIBS		= -lQtCore -lQtGui -lQtNetwork -lqwt -lMinuit2 -lgomp -lxml++-2.6
INCLUDES	= -I /usr/include/Qt -I /usr/include/QtCore -I /usr/include/QtGui -I /usr/include/qwt


all: cascade nicosmodules



###################### cascade-qt-client ################
cascade: cascade.o cascadedialogs.o bins.o cascadewidget.o tofloader.o tofdata.o config.o histogram_item.o client.o helper.o logger.o
	$(COMPILER) $(FLAGS) $(LIBS) -o cascade cascade.o cascadedialogs.o bins.o cascadewidget.o tofloader.o tofdata.o config.o histogram_item.o client.o helper.o logger.o
#########################################################




###################### CPP-Dateien ######################
cascade.o: cascade.cpp cascade.moc cascadedialogs_moc.cpp cascadedialogs.moc bins.h parse.h ErrorBarPlotCurve.h tofdata.h cascadedialogs.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o cascade.o cascade.cpp

cascadedialogs.o: cascadedialogs_moc.cpp cascadedialogs.h cascadedialogs.moc 
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o cascadedialogs.o cascadedialogs_moc.cpp

bins.o: bins.cpp bins.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o bins.o bins.cpp

cascadewidget.o: cascadewidget_moc.cpp cascadewidget.h cascadewidget.moc
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o cascadewidget.o cascadewidget_moc.cpp

tofloader.o: tofloader.cpp tofloader.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o tofloader.o tofloader.cpp

tofdata.o: tofdata.cpp tofdata.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o tofdata.o tofdata.cpp

config.o: config.cpp config.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o config.o config.cpp

histogram_item.o: histogram_item.cpp histogram_item.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o histogram_item.o histogram_item.cpp

client.o: client_moc.cpp client.h client.moc
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o client.o client_moc.cpp

helper.o: helper.cpp helper.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o helper.o helper.cpp

logger.o: logger.cpp logger.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o logger.o logger.cpp
#########################################################



############################ Dialoge ############################
cascadedialogs.h: ui_calibrationdlg.h ui_sumdialog.h ui_serverdlg.h ui_servercfgdlg.h ui_graphdlg.h

ui_calibrationdlg.h: calibrationdlg.ui
	uic calibrationdlg.ui > ui_calibrationdlg.h

ui_sumdialog.h: sumdialog.ui
	uic sumdialog.ui > ui_sumdialog.h

ui_serverdlg.h: serverdlg.ui
	uic serverdlg.ui > ui_serverdlg.h

ui_servercfgdlg.h: servercfgdlg.ui
	uic servercfgdlg.ui > ui_servercfgdlg.h

ui_graphdlg.h: graphdlg.ui
	uic graphdlg.ui > ui_graphdlg.h
#################################################################



###################### MOC-Dateien ######################
cascade.moc:
	moc cascade.cpp -o cascade.moc


cascadewidget_moc.cpp: cascadewidget.cpp cascadewidget.moc
	cat cascadewidget.cpp cascadewidget.moc > cascadewidget_moc.cpp

cascadewidget.moc:
	moc cascadewidget.h -o cascadewidget.moc


cascadedialogs_moc.cpp: cascadedialogs.cpp cascadedialogs.moc
	cat cascadedialogs.cpp cascadedialogs.moc > cascadedialogs_moc.cpp

cascadedialogs.moc:
	moc cascadedialogs.h -o cascadedialogs.moc


client_moc.cpp: client.cpp client.moc
	cat client.cpp client.moc > client_moc.cpp

client.moc:
	moc client.h -o client.moc
#########################################################




###################### clean ######################
# Qt-Client
clean_qt:
	rm -f *.moc *_moc.cpp
	rm -f ui_*.h
	rm -f *~
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

nicosclient/libcascadeclient.a:
	cd nicosclient && qmake && make

nicosclient/pythonbinding/cascadeclient.so: nicosclient/pythonbinding/cascadeclient.sip nicosclient/libcascadeclient.a
	cd nicosclient/pythonbinding && python configure.py && make

nicoswidget/libcascadewidget.a:
	-cd nicoswidget && qmake && make

nicoswidget/pythonbinding/cascadewidget.so: nicoswidget/pythonbinding/cascadewidget.sip nicoswidget/libcascadewidget.a
	-cd nicoswidget/pythonbinding && python configure.py && make
##########################################################
