PYTHON ?= python
PROFILE ?= full
OUTPUT ?= results/$(PROFILE)
RUN = $(PYTHON) -m src.simulation
ARGS = --profile $(PROFILE) --output "$(OUTPUT)"

.PHONY: all simulate analyze figures clean test smoke

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

smoke:
	$(RUN) all --profile smoke --output results/smoke
