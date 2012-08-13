
test1:
	PYTHONPATH=billy:. python tests/tests/kansas_tests.py TestKansas.test_committees

flake :
	~/.local/bin/flake8 .
