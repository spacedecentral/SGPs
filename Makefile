# Rules to only make the required HTML versions, not all of them,
# without the user having to keep track of which.
#
# Not really important, but convenient.

SEP2HTML=sep2html.py

PYTHON=python3

.SUFFIXES: .txt .html .rst

.txt.html:
	@$(PYTHON) $(SEP2HTML) $<

.rst.html:
	@$(PYTHON) $(SEP2HTML) $<

TARGETS= $(patsubst %.rst,%.html,$(wildcard sep-????.rst)) $(patsubst %.txt,%.html,$(wildcard sep-????.txt)) sep-0000.html

all: sep-0000.rst $(TARGETS)

$(TARGETS): sep2html.py

sep-0000.rst: $(wildcard sep-????.txt) $(wildcard sep-????.rst) $(wildcard sep0/*.py) gensepindex.py
	$(PYTHON) gensepindex.py .

# rss:
# 	$(PYTHON) sep2rss.py .

# install:
# 	echo "Installing is not necessary anymore. It will be done in post-commit."

# clean:
# 	-rm sep-0000.rst
# 	-rm sep-0000.txt
# 	-rm *.html

# update:
# 	git pull https://github.com/spacedecentral/seps.git

# venv:
# 	$(PYTHON) -m venv venv
# 	./venv/bin/python -m pip install -U docutils
