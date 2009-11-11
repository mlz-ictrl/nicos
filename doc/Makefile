# Build only changed doc files.

.SUFFIXES: .txt .html

.txt.html:
	rst2html --stylesheet-path=style.css --link-stylesheet $< $@

TARGETS=$(patsubst %.txt,%.html,$(wildcard *.txt))

all: $(TARGETS)

clean:
	rm *.html
