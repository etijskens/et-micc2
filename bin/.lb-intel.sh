#!/bin/bash
# Intel Python 3 distribution 
module load leibniz/supported
module load gh
module load buildtools
module load IntelPython3-Packages

# A temporary workaround for getting the correct f2py
export PATH=${EBROOTPYTHON}/bin/:$PATH
# the workaround does not work for the tests

