tbilly:
	PYTHONPATH=billy:. billy/billy/bin/update.py ks

alltests:
	PYTHONPATH=billy:. python tests/run_all_tests.py

test1:
	PYTHONPATH=billy:. python tests/tests/kansas_tests.py TestKansas.test_committees

flake :
	~/.local/bin/flake8 .
