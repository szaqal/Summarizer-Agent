.PHONY: download-signal-cli install run

SHELL := /bin/bash

SIGNAL_CLI_VERSION = 0.14.5
SIGNAL_CLI_URL     = https://github.com/AsamK/signal-cli/releases/download/v$(SIGNAL_CLI_VERSION)/signal-cli-$(SIGNAL_CLI_VERSION)-Linux-client.tar.gz

download-signal-cli:
	mkdir -p bin
	wget -O /tmp/signal-cli.tar.gz $(SIGNAL_CLI_URL)
	tar -xzf /tmp/signal-cli.tar.gz -C bin --strip-components=1
	rm /tmp/signal-cli.tar.gz

install:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

run: install
	PATH=./bin:$$PATH .venv/bin/python -m summarizer_agent.main
