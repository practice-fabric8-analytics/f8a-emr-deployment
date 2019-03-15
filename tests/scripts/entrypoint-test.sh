#!/usr/bin/env bash

# test coverage threshold
COVERAGE_THRESHOLD=0

locale charmap

export RADONFILESENCODING=UTF-8

echo "*****************************************"
echo "*** Cyclomatic complexity measurement ***"
echo "*****************************************"
radon cc -s -a -i usr .

echo "*****************************************"
echo "*** Maintainability Index measurement ***"
echo "*****************************************"
radon mi -s -i usr .

echo "*****************************************"
echo "*** Unit tests ***"
echo "*****************************************"

pytest --cov=/src/ --cov-report term-missing --cov-fail-under=$COVERAGE_THRESHOLD -vv /tests/
codecov --token=4cae7f0b-5a20-49a8-a824-a4acd77f9ea1
