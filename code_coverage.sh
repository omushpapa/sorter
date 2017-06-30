#! /usr/bin/env bash
coverage erase
coverage run --source=. --omit=*/sorter/gui/* -m unittest discover -s tests/
coverage xml
python-codacy-coverage -r coverage.xml