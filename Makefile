.PHONY: download-signal-cli install register verify run

SHELL := /bin/bash

SIGNAL_CLI_VERSION = 0.14.5
SIGNAL_CLI_URL     = https://github.com/AsamK/signal-cli/releases/download/v$(SIGNAL_CLI_VERSION)/signal-cli-$(SIGNAL_CLI_VERSION)-Linux-client.tar.gz

download-signal-cli:
	mkdir -p bin
	wget -O /tmp/signal-cli.tar.gz $(SIGNAL_CLI_URL)
	tar -xzf /tmp/signal-cli.tar.gz -C bin/
	mv bin/signal-cli-client bin/signal-cli
	chmod +x bin/signal-cli
	rm /tmp/signal-cli.tar.gz

install:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

register:
	source .env && ./bin/signal-cli -a $$SIGNAL_SENDER register

verify:
	@test -n "$(CODE)" || (echo "Usage: make verify CODE=<verification-code>" && exit 1)
	source .env && ./bin/signal-cli -a $$SIGNAL_SENDER verify $(CODE)

run:
	PATH=./bin:$$PATH .venv/bin/python -m summarizer_agent.main
