# Build only changed doc files.

.SUFFIXES: .txt .html

.txt.html:
	rst2html --stylesheet-path=style.css --embed-stylesheet $< $@

TARGETS=$(patsubst %.txt,%.html,$(wildcard *.txt))

all: $(TARGETS)

$(TARGETS): style.css

