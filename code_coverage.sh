#! /usr/bin/env bash
pipenv run coverage erase
pipenv run coverage run --source=. --omit=*/sorter/gui/* -m unittest discover -s tests/
pipenv run coverage xml
pipenv run python-codacy-coverage -r coverage.xml