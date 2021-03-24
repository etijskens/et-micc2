rm -rf  ../foo
micc -p ../foo create --package
micc -p ../foo add pym --py
micc -p ../foo add bar --f2py
micc -p ../foo add baz --cpp
