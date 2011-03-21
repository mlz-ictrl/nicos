#
# Makefile für den Cascade-Qt-Client
#

COMPILER	= gcc
FLAGS		= -O2 -D __CASCADE_QT_CLIENT__
LIBS		= -lQtCore -lQtGui -lQtNetwork -lqwt -lMinuit2 -lgomp -lxml++-2.6
INCLUDES	= -I /usr/include/Qt -I /usr/include/QtCore -I /usr/include/QtGui

all: cascade



###################### cascade ##########################
cascade: cascade.o cascadewidget.o tofloader.o tofdata.o config.o histogram_item.o client.o
	$(COMPILER) $(FLAGS) $(LIBS) -o cascade cascade.o cascadewidget.o tofloader.o tofdata.o config.o histogram_item.o client.o
#########################################################




###################### CPP-Dateien ######################
cascade.o: cascade.cpp cascade.moc cascadedialoge.cpp cascadedialoge.moc bins.h parse.h ErrorBarPlotCurve.h tofdata.h
	$(COMPILER) $(FLAGS) $(INCLUDES) -c -o cascade.o cascade.cpp

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

cascadedialoge.moc:
	moc cascadedialoge.cpp -o cascadedialoge.moc

client.moc:
	moc client.h -o client.moc
#########################################################




###################### clean ######################
clean:
	rm *.moc
	rm *.o
	rm cascade
###################################################
