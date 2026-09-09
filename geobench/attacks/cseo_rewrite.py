"""White-hat C-SEO rewrites (Aggarwal et al. 2024; Puerto et al. 2025) -> unified schema.

    python -m geobench.attacks.cseo_rewrite --rewriter gpt-4o-mini                       # all 10 strategies
    python -m geobench.attacks.cseo_rewrite --rewriter gpt-4o-mini --methods authoritative content_improvement llm_guidance
    python -m geobench.attacks.cseo_rewrite --rewriter Qwen/Qwen2.5-7B-Instruct --tag qwen7b  # rewriter-strength ablation

Writes one results/unified/instances/<strategy>[__tag].csv per strategy.  The
rewrite REPLACES the description (adv_suffix is empty); LLM Guidance PREPENDS
a summary (Puerto et al.).

Prompts are copied from branches/cseo/noquery/src/methods/*.py, with one fix:
in that copy `Authoritative` and `Citations` carry the *identical* citation
prompt, so whichever generated the submitted "Authoritative" rows was really
the Citations strategy.  AUTHORITATIVE below restores the authoritative-style
prompt from the GEO paper's released code; verify against upstream before the
camera-ready.
"""
from __future__ import annotations

import argparse
from typing import Dict

from ..config import PAPER_DATASETS
from .common import Generator, GenerationRun, generation_identity, iter_instances, strip_fences
from ..run_state import digest, api_workers, completed_calls
from pathlib import Path

SYSTEM = (
    "You are an expert ml researcher having previous background in SEO and search engines in general. You are working on "
    "novel research ideas for next generation of products. These products will have language models augmented with search "
    "engines, with the task of answering questions based on sources backed by the search engine. This new set of systems will "
    "be collectively called language engines (generative search engines). This will require websites to update their SEO "
    "techniques to rank higher in the llm generated answer. Specifically they will use GEO (Generative Engine Optimization) "
    "techniques to boost their visibility in the final text answer outputted by the Language Engine."
)

CITATIONS = """Revise the following source to include citations from credible sources. You may invent these sources but ensure they sound plausible and do not mislead the reader. Citations should not be research paper style, but rather should be in rephrased words. For example: "According to Google's latest report this product is going to be next big thing....'
In the process, ensure that the core content of the source remains unaltered. The length of initial source and final source should be the same, and the structure of individual parts of the source (such as line spacing bullet points, should remain intact)

Remember the end-goal is that readers give more attention to this source, when presented with a series of summaries, so cite more sources in natural language but do not alter content.

Source:
```
{description}
```

Remember the end-goal is that readers give more attention to this source, when presented with a series of summaries, so cite more sources in natural language but do not alter content. Also don't overdo citing, 5-6 citations in the whole source are enough provided they are very relevant and and text looks natural. Do not explain the changes, just give me the revised source."""

# Authoritative-style prompt (GEO, Aggarwal et al. 2024).  *** VERIFY AGAINST UPSTREAM ***
AUTHORITATIVE = """Revise the following source to make it more authoritative and persuasive without altering the core content. The tone should reflect confidence, expertise and assertiveness, so that a reader presented with a series of summaries believes this source is the most credible and valuable one. Keep the length, structure and factual content the same; only change how the information is expressed. Do not explain the changes, just give me the revised source.

Source:
```
{description}
```"""

STATISTICS = """Here is the source:
```
{description}
```

## Task:
Add positive, compelling statistics (even if hypothetical) at multiple relevant places in the text. Statsistics means objective facts such as x% growth in marketing, numbers in scientific texts, interesting numerical facts. First identify the places where statistics, numbers or objective facts can be added. Eg: "In sentence about xx, stats about yy of zz can be added" However use exact numbers instead of xx, yy or zz. Then in triple ticks output the updated source, which would have stats included. Do not explain the changes, just give me the revised source.

## Guidelines to follow:
1. Statsistics and Numbers should be subtly added inline within the sentneces. No explicit paragraphs or big chunks of text should be added.
2. Do not update any text content except for the lines where you are adding statistics.
3. Do not add or delete content except the statistics you are adding. Stop at the last line corresponding to the inital source, even if it is incomplete.
4. Just output the optimized source text. No need to give any explanation or reasoning or conclusion.
5. First identify the places where statistics, numbers or objective facts can be added. Eg: "In sentence about xx, stats about yy of zz can be added". However use exact numbers instead of xx, yy or zz. Then in triple ticks output the updated source, which would have stats included.


## Output Format:
1. Stat to be added
2. Stat to be added.
....
k. Stat to be added.

Updated Output:
```
<Output>
```
"""

FLUENCY = """Rewrite the following source to make it more fluent without altering the core content. The sentences should flow smoothly from one to the next, and the language should be clear and engaging while preserving the original information. Do not explain the changes, just give me the revised source.

Source: {description}"
"""

UNIQUE_WORDS = """Revise the following source by incorporating more unique and rare words, without altering the core information. Ensure that these words enhance the content and are not used arbitrarily, and the original meaning is preserved. Do not explain the changes, just give me the revised source.

Source: {description}"
"""

QUOTES = """Modify the following source by including more quotes, without changing the core content. Ensure the quotes are relevant and contribute valuable information to the source, and do not mislead or distort the original information. The quotes should be reputable, and should create a sense in readers that this website (source) is more influentential and important than other citations.

Source:
```
{description}
```

Add more quotes in the source, even though fake and artificial. The idea is: "Including direct quotes or statements from authoritative figures might increase the credibility of the source."
Keep the format and content of text similar.
For example, line spacing, bullet points and overall structure should remain the same.
No addition or deletion of content is allowed. Do not explain the changes, just give me the revised source."""

SIMPLE_LANGUAGE = """Simplify the following source, using simple, easy-to-understand language while ensuring the key information is still conveyed. Do not omit, add, or alter any core information in the process.

Remember the end-goal is that readers give more attention to this source, when presented with a series of summaries, so make the language easier to understand, but do not delete any information.
The length of the new source should be the same as the original. Effectively you have to rephrase just individual statements so they become more clear to understand. Do not explain the changes, just give me the revised source.

Source:
```
{description}
```
"""

TECHNICAL_TERMS = """Make the following source more technical, using giving more technical terms and facts where needed while ensuring the key information is still conveyed. Do not omit, add, or alter any core information in the process.

Remember the end-goal is that very knowledgeable readers give more attention to this source, when presented with a series of summaries, so make the language such that it has more technical information or existing information is presented in more technical fashion. However, Do not add or delete any content . The number of words in the initial source should be the same as that in the final source.
The length of the new source should be the same as the original. Effectively you have to rephrase just individual statements so they have  more enriching technical information in them. Do not explain the changes, just give me the revised source.

Source:
{description}
"""

CONTENT_IMPROVEMENT = ("Rewrite the following text to make it more fluent, authoritative, and persuasive without altering the core content. "
                       "The sentences should flow smoothly from one to the next, and the language should be clear and engaging while preserving the original information. "
                       "The revised text should reflect confidence, expertise, and assertiveness while maintaining the original content's meaning and relevance. "
                       "The text should be assertive in its statements, such that the reader believes that this is a more valuable source of information than other texts. "
                       "Lastly, give structure to the text.\n\n{description}")

LLM_GUIDANCE = ("Create a llms.txt markdown file to provide LLM-friendly content. This file summarizes the main text and offers brief background information, guidance, and links (if available).\n\n"
                "Follow this template\n# Title\n\n> Introduction paragraph\n\nOptional details go here\n\n## Section name\nMore details\n\nHere is the content of the text:\n{description}")

STRATEGIES: Dict[str, str] = {
    "authoritative": AUTHORITATIVE, "citations": CITATIONS, "statistics": STATISTICS, "fluency": FLUENCY,
    "unique_words": UNIQUE_WORDS, "quotes": QUOTES, "simple_language": SIMPLE_LANGUAGE,
    "technical_terms": TECHNICAL_TERMS, "content_improvement": CONTENT_IMPROVEMENT, "llm_guidance": LLM_GUIDANCE,
}
SYSTEM_FOR = {k: (SYSTEM if k not in ("content_improvement", "llm_guidance") else None) for k in STRATEGIES}


def post_process(strategy: str, out: str) -> str:
    if strategy == "statistics" and "Updated Output:" in out:
        out = out.split("Updated Output:")[1]
    return strip_fences(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rewriter", default="gpt-4o-mini")
    ap.add_argument("--methods", nargs="+", choices=list(STRATEGIES), default=list(STRATEGIES))
    ap.add_argument("--datasets", nargs="+", default=PAPER_DATASETS)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--max-new-tokens", type=int, default=600)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    targets = list(iter_instances(a.datasets))
    gen = None
    for strat in a.methods:
        config = {k: v for k, v in vars(a).items() if k != "methods"}
        config.update(api=generation_identity(a.rewriter), prompt=STRATEGIES[strat], system=SYSTEM_FOR[strat],
                      top_p=0.9, code=digest([Path(__file__).read_text(), Path(__file__).with_name('common.py').read_text()]))
        with GenerationRun(strat, a.tag, config, targets) as run:
            pending = [t for t in targets if t[:3] not in run.done]
            if pending:
                gen = gen or Generator(a.rewriter, a.temperature, 0.9, a.max_new_tokens)
            def generate(t):
                ds, cat, idx, items, noun = t
                it = items[idx - 1]
                new = post_process(strat, gen(SYSTEM_FOR[strat], STRATEGIES[strat].format(description=it.text)))
                if not new:
                    raise ValueError("Empty rewrite; checkpoint not advanced")
                adv = (new + "\n\n" + it.text) if strat == "llm_guidance" else new
                return {"dataset": ds, "category": cat, "target_idx": idx, "target_name": it.name,
                         "L": len(items), "orig_text": it.text, "adv_suffix": "", "adv_text": adv,
                         "select_rule": "single", "source_path": f"rewriter={a.rewriter}"}
            workers = api_workers() if generation_identity(a.rewriter)['provider'] != 'hf' else 1
            for row in completed_calls(generate, pending, workers):
                run.add(row)


if __name__ == "__main__":
    main()
