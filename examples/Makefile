EXAMPLES=$(wildcard *.py)
PDFS = $(patsubst %.py,%.pdf,$(EXAMPLES))

.PHONY: all clean

all: $(PDFS)

%.pdf: %.py
	python $<

clean:
	rm -f *.pdf *.svg *.tex
