Cascade-Qt-Client (/data/software/Cascade)
==========================================

Unterverzeichnis ./nicosobj: Kommunikation mit Server per Nicos
Unterverzeichnis ./nicoswidget: Lib für graphische Darstellung


* Qt-Version kompilieren mit:
----------------------------
(neue Methode): 
	mit "make"

oder (alte):
	moc cascade.cpp -o cascade.moc
	moc cascadedialoge.cpp -o cascadedialoge.moc
	moc client.h -o client.moc

	gcc -D __CASCADE_QT_CLIENT__ -O2 -I /usr/include/qwt/ -I /usr/include/Qt -I /usr/include/QtCore -I /usr/include/QtGui -o cascade cascade.cpp tofloader.cpp config.cpp histogram_item.cpp client.cpp -lQtCore -lQtGui -lQtNetwork -lqwt -lMinuit2 -lgomp -lxml++-2.6


* Nicos-Version kompilieren mit:
-------------------------------
neu: unter ./nicosobj		(analog für /nicoswidget):
	qmake
	make
     unter ./nicosobj/pythonbinding
	python ./configure.py
	make

alt: 
	gcc -O2 -I /usr/include/qwt/ -I /usr/include/Qt -I /usr/include/QtCore -I /usr/include/QtGui -o nicosclient nicosclient.cpp tofloader.cpp config.cpp client.cpp -lQtCore -lQtGui -lQtNetwork -lMinuit2 -lgomp


* Kommandozeilenversion kompilieren mit:
---------------------------------------
gcc -O2 -I /usr/include/Qt -I /usr/include/QtGui -I /usr/include/QtCore -o tofloader plot.cpp config.cpp tofloader.cpp -lqwtplot3d -lqwt -lMinuit2 -lgomp -lxml++-2.6



* IGOR-Version kompilieren mit:
------------------------------
#define IGOR_PLUGIN in tofloader.h setzen

TODO

IGOR-Version - Aufruf:
---------------------
SimpleLoadWave /P=pathName /F=fileName params={Fkt, Parameter1, Parameter2, ...}

pathName ist der interne IGOR-Bezeichner für einen Pfad, fileName der Dateiname innerhalb dieses 
Pfades.


Fkt=0: PAD-Datei laden
	keine Parameter

Fkt=1: 2D-Bild ausgeben
	6 Parameter:
		Parameter1: ROI-x-Start
		Parameter2: ROI-x-Ende
		Parameter3: ROI-y-Start
		Parameter4: ROI-y-Ende
		Parameter5: Welche Folie [0..3]
		Parameter6: Welcher Zeitkanal dieser Folie [0..15]

Fkt=2: 1D-Graph ausgeben (Pixel der einzelnen Bilder der Folie zusammenzählen)
	5 Parameter:
		Parameter1: ROI-x-Start
		Parameter2: ROI-x-Ende
		Parameter3: ROI-y-Start
		Parameter4: ROI-y-Ende
		Parameter5: Welche Folie [0..3]

Fkt=3: Folien anhand von Bitfeldern zusammenzählen
	2 Parameter:
		Parameter1: Welche Folien sollen gezählt werden
		Parameter2: Welche Zeitkanäle sollen gezählt werden


* Fragen an:
-----------
tweber@frm2.tum.de

