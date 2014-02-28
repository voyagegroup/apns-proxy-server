.PHONY: run

help:
	@echo "Please [make setup] first."
	@echo "After python environment created, activate local python by [source ./python/bin/activate]"

setup:
	virtualenv . --no-site-packages
	./bin/pip install -r requirements.txt
	chmod -R g+w .


lint:
	flake8 apns-proxy-server

run: clean
	./bin/python -m apns-proxy-server.invoker

live_test: clean
	./bin/python -m test.live_test

clean:
	-rm apns-proxy-server/**/*.pyc
	-rm settings.pyc
