#!/bin/bash

cd ~/workspace/

python et-rstor/tests/test_et_rstor.py TutorialGettingStarted
python et-rstor/tests/test_et_rstor.py TutorialProject_et_dot_1
python et-rstor/tests/test_et_rstor.py TutorialProject_et_dot_2
python et-rstor/tests/test_et_rstor.py TutorialProject_et_dot_3
python et-rstor/tests/test_et_rstor.py TutorialProject_et_dot_4
python et-rstor/tests/test_et_rstor.py TutorialProject_et_dot_5
python et-rstor/tests/test_et_rstor.py TutorialProject_et_dot_6
python et-rstor/tests/test_et_rstor.py TutorialProject_et_dot_7
python et-rstor/tests/test_et_rstor.py TutorialProject_et_dot_8

cd et-micc2
# go for a clean build
rm -rf docs/_build
micc2 doc