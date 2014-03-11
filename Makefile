.PHONY: run

help:
	@echo "Please [make setup] first."
	@echo "After python environment created, activate local python by [source ./python/bin/activate]"

setup_dev:
	virtualenv . --no-site-packages
	./bin/pip install -r requirements_dev.txt
	chmod -R g+w .

lint:
	./bin/flake8 apns_proxy_server

run: clean
	./bin/python -m apns_proxy_server.invoker

test: clean
	./bin/nosetests

clean:
	-rm apns_proxy_server/**/*.pyc
	-rm tests/**/*.pyc
	-rm settings.pyc

setup_prod:
	virtualenv . --no-site-packages
	./bin/pip install --upgrade pip
	./bin/pip install --upgrade setuptools
	./bin/pip install wheel
	./bin/pip install --no-deps wheelhouse/*

create_wheels:
	virtualenv . --no-site-packages
	-mkdir wheelhouse
	-rm wheelhouse/*
	./bin/pip install --upgrade pip
	./bin/pip install --upgrade setuptools
	./bin/pip install wheel
	./bin/pip wheel --wheel-dir=./wheelhouse -r requirements_prod.txt
