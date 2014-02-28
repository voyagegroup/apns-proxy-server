.PHONY: run

help:
	@echo "Please [make setup] first."
	@echo "After python environment created, activate local python by [source ./python/bin/activate]"

setup:
	virtualenv . --no-site-packages
	./bin/pip install -r requirements.txt
	chmod -R g+w .


lint:
	flake8 apns_proxy_server

run: clean
	./bin/python -m apns_proxy_server.invoker

test: clean
	./bin/nosetests

live_test: clean
	./bin/python -m tests.live_test

clean:
	-rm apns_proxy_server/**/*.pyc
	-rm settings.pyc
