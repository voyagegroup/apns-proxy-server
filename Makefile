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

many_token_test: clean
	./bin/python -m tests.many_token_test

connection_keep_test: clean
	./bin/python -m tests.connection_keep_test

clean:
	-rm apns_proxy_server/**/*.pyc
	-rm tests/**/*.pyc
	-rm settings.pyc
