.PHONY: run

help:
	@echo "Please [make setup] first."
	@echo "After python environment created, activate local python by [source ./python/bin/activate]"

setup:
	virtualenv . --no-site-packages
	./bin/pip install -r requirements_prod.txt
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
