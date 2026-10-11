# GEO-Bench revision pipeline.  `make help` lists targets.
SHELL := /bin/bash
RANKER ?= llama-3.1-8b
K ?= 10
RANKERS ?= llama-3.1-8b qwen2.5-14b mistral-7b gpt-4o-mini

help:
	@grep -E '^[a-z_-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-16s %s\n", $$1, $$2}'

setup:          ## create venv, install deps, write manifests
	bash scripts/00_setup.sh

manifests:      ## (re)write manifests/<dataset>.csv
	python -m geobench.data

collect:        ## pull existing raw outputs (StealthRank/Zero-Shot/RAF/STS) into the unified schema + failure scan
	bash scripts/01_collect_existing.sh

attacks:        ## regenerate inference-only attacks (Zero-Shot, C-SEO rewrites, TAP)
	bash scripts/02_generate_attacks.sh

ablation:       ## attacker/rewriter-strength ablation
	bash scripts/02_generate_attacks.sh ablation

evaluate:       ## score all instances with $(RANKER) (K=$(K)) + stats
	bash scripts/03_evaluate.sh $(RANKER) $(K)

evaluate-all:   ## evaluate with every ranker in $(RANKERS) sequentially (use scripts/slurm for the cluster)
	for r in $(RANKERS); do bash scripts/03_evaluate.sh $$r $(K); done

detect:         ## LLM-judge, relevance drift, cross-encoder reranker
	bash scripts/04_detect.sh

stats:          ## bootstrap CIs + Wilcoxon for $(RANKER)
	python -m geobench.stats --ranker $(RANKER)

tables:         ## Table 4 / cross-ranker table / Figure 1 / appendix
	RANKERS="$(RANKERS)" bash scripts/05_tables.sh

scan:           ## coverage + degenerate-run report
	python -m geobench.scan_failed_runs results/unified/instances/*.csv

test:           ## offline unit tests (no GPU, no network)
	python -m pytest -q tests

.PHONY: help setup manifests collect attacks ablation evaluate evaluate-all detect stats tables scan test
