#!/bin/bash

# Execute this script in a micc project to test micc and micc-build on the current project.
# Any changes in:
#   . ~/software/dev/workspace/et-micc2/et_micc2/
# will be immediately visible in the project's virtual environment.

# Behaviour: The script replaces the installed python package et_micc2
# if present, with symbolic links to ~/software/dev/workspace/et-micc2/et_micc2/
# If the current project is et_micc2
# message and exits.


current_project=$(micc2 info --name)

if [[ "$current_project" = et_micc2 ]]
then
  echo "ERROR: it is not allowed to do this in project et_micc2"
  exit 1
fi

# The location of the et-micc2 project
# (adjust this to your needs):
workspace="/Users/etijskens/software/dev/workspace"

site_packages=$(python -c 'import site; print(site.getsitepackages()[0])')
cd ${site_packages}
#echo "site-packages = ${site_packages}"

if [[ -d et_micc2 ]]
then
  echo "sym-linking ~/software/dev/workspace/et-micc2/et_micc2/"
  rm -rf et_micc2
  ln -s ${workspace}/et-micc2/et_micc2/
else
  echo "WARNING: micc2 is not installed in the current project, hence it cannot be sym-linked for testing."
  echo "         You may want to run 'pip install et-micc2' first, and rerun the script."
fi
