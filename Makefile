.PHONY: lint test

lint:
	python -m pylint check_mumble_ping

test:
	python -m unittest -v test_check_mumble_ping.py
coverage:
	python -m coverage run -m unittest test_check_mumble_ping.py
	python -m coverage report -m --include check_mumble_ping.py
