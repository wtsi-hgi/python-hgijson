#!/usr/bin/env bash
pip install -q -r requirements.txt
pip install -q -r test_requirements.txt

nosetests -v --with-coverage --cover-package=hgijson --cover-html
