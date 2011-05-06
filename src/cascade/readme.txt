Cascade-Qt-Client (/data/software/Cascade)
==========================================

Unterverzeichnis ./nicosobj: Kommunikation mit Server per Nicos
Unterverzeichnis ./nicoswidget: Lib für graphische Darstellung


* Qt-Version kompilieren mit:
----------------------------
(neue Methode): 
	make clean
	make

oder (alte):
	moc cascade.cpp -o cascade.moc
	moc cascadedialogs.cpp -o cascadedialogs.moc
	moc client.h -o client.moc

	gcc -D __CASCADE_QT_CLIENT__ -O2 -I /usr/include/qwt/ -I /usr/include/Qt -I /usr/include/QtCore -I /usr/include/QtGui -o cascade cascade.cpp tofloader.cpp config.cpp histogram_item.cpp client.cpp -lQtCore -lQtGui -lQtNetwork -lqwt -lMinuit2 -lgomp -lxml++-2.6


* Nicos-Module kompilieren mit:
------------------------------
neu: unter ./nicosobj		(analog für /nicoswidget):
	qmake
	make
     unter ./nicosobj/pythonbinding
	python ./configure.py
	make

oder: make nicosmodules

alt: 
	gcc -O2 -I /usr/include/qwt/ -I /usr/include/Qt -I /usr/include/QtCore -I /usr/include/QtGui -o nicosclient nicosclient.cpp tofloader.cpp config.cpp client.cpp -lQtCore -lQtGui -lQtNetwork -lMinuit2 -lgomp


* (uralte) Kommandozeilenversion kompilieren mit:
------------------------------------------------
gcc -O2 -I /usr/include/Qt -I /usr/include/QtGui -I /usr/include/QtCore -o tofloader plot.cpp config.cpp tofloader.cpp -lqwtplot3d -lqwt -lMinuit2 -lgomp -lxml++-2.6



* IGOR-Version kompilieren mit:
------------------------------
#define IGOR_PLUGIN in tofloader.h setzen

	TODO



* Fragen an:
-----------
tweber@frm2.tum.de
