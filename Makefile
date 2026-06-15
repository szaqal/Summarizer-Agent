.PHONY: download-signal-cli install link register verify run

SHELL := /bin/bash

SIGNAL_CLI_VERSION = 0.14.5
SIGNAL_CLI_URL     = https://github.com/AsamK/signal-cli/releases/download/v$(SIGNAL_CLI_VERSION)/signal-cli-$(SIGNAL_CLI_VERSION).tar.gz


download-signal-cli:
	mkdir -p signal-cli
	wget -O /tmp/signal-cli.tar.gz $(SIGNAL_CLI_URL)
	tar -xzf /tmp/signal-cli.tar.gz -C signal-cli/ --strip-components=1
	chmod +x signal-cli/bin/signal-cli
	rm /tmp/signal-cli.tar.gz

install:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

link:
	source ~/.sdkman/bin/sdkman-init.sh && sdk use java 25.0.2-open && source .env && ./signal-cli/bin/signal-cli link -n "Summarizer Agent"

register:
	@test -n "$(CAPTCHA)" || (echo "Usage: make register CAPTCHA=<captcha-token>" && exit 1)
	source ~/.sdkman/bin/sdkman-init.sh && sdk use java 25.0.2-open && source .env && ./signal-cli/bin/signal-cli -a $$SIGNAL_SENDER register --captcha $(CAPTCHA)

verify:
	@test -n "$(CODE)" || (echo "Usage: make verify CODE=<verification-code>" && exit 1)
	source ~/.sdkman/bin/sdkman-init.sh && sdk use java 25.0.2-open && source .env && ./signal-cli/bin/signal-cli -a $$SIGNAL_SENDER verify $(CODE)

run:
	PATH=./signal-cli/bin:$$PATH .venv/bin/python -m summarizer_agent.main
