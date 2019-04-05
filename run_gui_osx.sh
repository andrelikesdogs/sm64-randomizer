#!/bin/bash
# only required so I can test the gui.py on MacOSX

# what real Python executable to use
PYVER=3.7.2
PYTHON=~/.pyenv/versions/3.7.2/bin/python

# find the root of the virtualenv, it should be the parent of the dir this script is in
ENV=`$PYTHON -c "import os; print(os.path.abspath(os.path.join(os.path.dirname(\"$0\"))))"`

# now run Python with the virtualenv set as Python's HOME
export PYTHONHOME=$ENV 
exec $PYTHON "$@"
