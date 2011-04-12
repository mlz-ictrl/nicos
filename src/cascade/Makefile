#
# Makefile für den Cascade-Qt-Client
#

COMPILER	= gcc
FLAGS		= -O2 -D __CASCADE_QT_CLIENT__
LIBS		= -lQtCore -lQtGui -lQtNetwork -lqwt -lMinuit2 -lgomp -lxml++-2.6
INCLUDES	= -I /usr/include/Qt -I /usr/include/QtCore -I /usr/include/QtGui

all: cascade



###################### cascade ##########################
cascade: cascade.o cascadedialogs.o bins.o cascadewidget.o tofloader.o tofdata.o config.o histogram_item.o client.o
	$(COMPILER) $(FLAGS) $(LIBS) -o cascade cascade.o cascadedialogs.o bins.o cascadewidget.o tofloader.o tofdata.o config.o histogram_item.o client.o
#########################################################




###################### CPP-Dateien ######################
cascade.o: cascade.cpp cascade.moc cascadedialogs.cpp cascadedialogs.moc bins.h parse.h ErrorBarPlotCurve.h tofdata.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o cascade.o cascade.cpp

cascadedialogs.o: cascadedialogs.cpp cascadedialogs.h cascadedialogs.moc
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o cascadedialogs.o cascadedialogs.cpp

bins.o: bins.cpp bins.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o bins.o bins.cpp

cascadewidget.o: cascadewidget.cpp cascadewidget.h cascadewidget.moc
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o cascadewidget.o cascadewidget.cpp

tofloader.o: tofloader.cpp tofloader.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o tofloader.o tofloader.cpp

tofdata.o: tofdata.cpp tofdata.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o tofdata.o tofdata.cpp

config.o: config.cpp config.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o config.o config.cpp

histogram_item.o: histogram_item.cpp histogram_item.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o histogram_item.o histogram_item.cpp

client.o: client.cpp client.h client.moc
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o client.o client.cpp
#########################################################




###################### MOC-Dateien ######################
cascade.moc:
	moc cascade.cpp -o cascade.moc

cascadewidget.moc:
	moc cascadewidget.h -o cascadewidget.moc

cascadedialogs.moc:
	moc cascadedialogs.h -o cascadedialogs.moc

client.moc:
	moc client.h -o client.moc
#########################################################




###################### clean ######################
clean:
	rm -f *.moc
	rm -f *.o
	rm -f cascade
	rm -f nicosclient/*.a nicosclient/pythonbinding/*.so
	rm -f nicoswidget/*.a nicoswidget/pythonbinding/*.so
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
