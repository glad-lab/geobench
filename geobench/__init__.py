"""GEO-Bench unified evaluation package (revision branch).

One protocol for every method:

    collect  -> geobench/collect.py   : pull the final adversarial text per instance
                                        out of each method's raw outputs
    evaluate -> geobench/evaluate.py  : re-rank every instance with ONE ranker,
                                        ONE prompt, K random orderings, and
                                        compute NRG / Success@a / Promote@a /
                                        KVR / PPL-R the same way for all methods
    detect   -> geobench/detect.py    : LLM-judge detectability, relevance drift,
                                        cross-encoder reranker score
    stats    -> geobench/stats.py     : bootstrap CIs and paired Wilcoxon tests
    tables   -> geobench/make_tables.py

All stages read/write flat CSVs under results/unified/ so any stage can be
re-run independently.
"""

__version__ = "0.2.0"
