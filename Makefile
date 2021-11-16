VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip3
CLEANUP = *.pyc

run: $(VENV)/bin/activate
	$(PYTHON) app.py


$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt


clean:
	python3 -m venv --clear $(VENV)
