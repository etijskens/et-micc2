#!/bin/bash
# build documentation
####################################################################################################
# Make sure we are in et-micc2 project directory:
dir_name="$(basename -- $PWD)"
if [ $dir_name == "et-micc2" ]; then
  echo "Building .rst files."
else
  echo "You must run this command from the project directory `et-micc2`."
  exit 255
fi

# build .rst files

python ./tutorials/rstor/TutorialGettingStarted.py
for i in {1..8}
do
   python ./tutorials/rstor/TutorialProject_et_dot.py $i
done
python ./tutorials/rstor/TutorialVCS.py
python ./tutorials/rstor/TutorialVersionManagement.py
python ./tutorials/rstor/TutorialPublish.py
python ./tutorials/rstor/TutorialDebugging.py

####################################################################################################
echo "Building documentation ..."
# go for a clean build
rm -rf docs/_build
cd ./docs
make html