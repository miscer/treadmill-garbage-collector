Python 3.5+ is required to run the code.

To run the tests, first make sure virtualenv is installed, create a new virtual
environment and activate it:

    virtualenv-3 venv
    source venv/bin/activate

Then install pytest:

    pip install pytest

Then run the tests:

    pytest

To run coverage analysis install coverage.py, run tests and generate the HTML
report:

    pip install coverage
    coverage -m pytest
    coverage html

The output will be in the htmlcov directory.
