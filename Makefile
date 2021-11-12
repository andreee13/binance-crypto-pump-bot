VENV = venv
PYTHON = $(VENV)/Scripts/python
PIP = $(VENV)/Scripts/pip3
CLEANUP = *.pyc

run: $(VENV)/Scripts/activate
	$(PYTHON) app.py


$(VENV)/Scripts/activate: requirements.txt
	py -m venv $(VENV)
	$(PIP) install -r requirements.txt


clean:
	py -m venv --clear $(VENV)
