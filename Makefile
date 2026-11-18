PYTHON ?= python
OUTPUT ?= results
RUN = $(PYTHON) -m src.simulation
ARGS = --output "$(OUTPUT)"

ifeq ($(OS),Windows_NT)
VENV_PYTHON = .venv/Scripts/python.exe
else
VENV_PYTHON = .venv/bin/python
endif

.PHONY: all simulate analyze figures clean test reproduce stability-check

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

reproduce: $(VENV_PYTHON)
	"$(VENV_PYTHON)" -m pip install -r requirements.txt
	"$(VENV_PYTHON)" -m src.simulation all $(ARGS)
	"$(VENV_PYTHON)" -m unittest discover -s tests -v
	"$(VENV_PYTHON)" $(CHECK_RESULTS)

$(VENV_PYTHON):
	$(PYTHON) -m venv .venv

stability-check:
	$(PYTHON) $(CHECK_RESULTS)

CHECK_RESULTS = -c "import os; exec(os.environ['UNIT2_CHECK_RESULTS'])" "$(OUTPUT)"
reproduce stability-check: export UNIT2_CHECK_RESULTS = $(VALIDATION_SCRIPT)

define VALIDATION_SCRIPT
import csv
from itertools import product
import json
from math import isfinite
from pathlib import Path
import sys

output = Path(sys.argv[1])
run = json.loads((output / 'run.json').read_text(encoding='utf-8'))
config = run['config']
remaining = set(product(config['regimes'], config['dimensions'], config['theta'],
                        range(config['replicates'])))
expected = len(remaining)
with (output / 'raw' / 'replicates.csv').open(newline='', encoding='utf-8') as handle:
    for row in csv.DictReader(handle):
        key = row['regime'], int(row['p']), float(row['theta']), int(row['replicate'])
        if key not in remaining:
            sys.exit(f'Duplicate or unexpected trial: {key}')
        remaining.remove(key)
        if not all(isfinite(float(value)) for field, value in row.items() if field != 'regime'):
            sys.exit(f'Nonfinite result: {key}')
        if row['convergence_warning'] != '0' or int(row['iterations']) >= config['max_iter']:
            sys.exit(f'Convergence issue: {key}')
if remaining or run['fits'] != expected:
    sys.exit('Saved trials do not match the run metadata and configuration.')
print(f'Stability check passed for {expected:,} trials.')
endef
