PYTHON ?= python
OUTPUT ?= results
RUN = $(PYTHON) -m src.simulation
ARGS = --output "$(OUTPUT)"

.PHONY: all simulate analyze figures clean test

all:
	$(RUN) all $(ARGS)

simulate:
	$(RUN) simulate $(ARGS)

analyze:
	$(RUN) analyze $(ARGS)

figures:
	$(RUN) figures $(ARGS)

clean:
	$(RUN) clean $(ARGS)

test:
	$(PYTHON) -m unittest discover -s tests -v
