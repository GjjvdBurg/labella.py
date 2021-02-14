EXAMPLES=$(wildcard *.py)
PDFS = $(patsubst %.py,%.pdf,$(EXAMPLES))
SVGS = $(patsubst %.py,%.svg,$(EXAMPLES))

.PHONY: all clean

all: $(PDFS) $(SVGS)

%.pdf %.svg &: %.py
	python $<

clean:
	rm -f *.pdf *.svg *.tex
