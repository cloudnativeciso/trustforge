# Makefile for Trustforge
# Usage overrides:
#   make pdf POLICY=policies/another.md
#   make OUT=build pdf

SHELL := /bin/zsh

.PHONY: install lint test pdf html index all clean open-pdf open-html control-map risk-demo

# Defaults
POLICY ?= policies/information-security-policy.md
OUT    ?= out

install:
	uv venv && uv pip install -e '.[dev]'

lint:
	uv run ruff check . && uv run mypy .

test:
	PYTHONPATH=src uv run pytest

pdf:
	uv run trustforge pdf $(POLICY)

html:
	uv run trustforge html $(POLICY)

index:
	uv run trustforge index --out $(OUT)/policies.csv

all: pdf html index

clean:
	rm -f $(OUT)/*.{aux,toc,out,lof,lot,log} 2>/dev/null || true
	rm -f $(OUT)/*.pdf $(OUT)/*.html $(OUT)/*.tex $(OUT)/*.body.tex $(OUT)/*.csv 2>/dev/null || true

open-pdf:
	open $(OUT)/$$(basename $(POLICY:.md=.pdf))

open-html:
	open $(OUT)/$$(basename $(POLICY:.md=.html))

control-map:
	uv run trustforge control-map nist-csf20 --out out/control_map.csv

risk-demo:
	uv run trustforge risk-export examples/risks.yaml --out out/risks.csv
