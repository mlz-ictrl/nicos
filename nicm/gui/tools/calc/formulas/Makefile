all: miezefml.png braggfml.png

%.png: %.tex
	latex `basename $@ .png`.tex
	dvipng -D 150 -T tight -o $@ `basename $@ .png`.dvi
	mogrify -border 5 -bordercolor white $@
	rm *.aux *.log *.dvi
