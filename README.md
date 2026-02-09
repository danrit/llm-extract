# LLM-Extract

Extract structured data from text content using LLMs.

DRAFT: more on the objective of this tool: it is built to run extraction the same structured data (`data_schemas.default`) in a list (`datasets.default`) of documents (`document_sets.default`) usings LLM and output tabular data. It is designed to run the extraction several times - or variations - (`scenarios.default.variations`) with different models, prompts or model options (temperature, top_p). It also designed to repeat one variation several times (reference to non-deterministic behaviour of LLMs...) (`scenarios.default.variations.repeat`).

Note: actually this is not limited to extraction of structured data (ie a task where the research data is already in the input document but drowned in it), but to any task which generate structured data (because then structured data can then be easily compared/assessed)

Note 2: maybe that tool is more aimed at smaller models (local or cloud-hosted). By design it will have to be run **very** repetitively on big dataset so cost of running huge models from the frontier labs can be dissuasive. But big models need to be tested too sometimes to make sure the small models jobs remains relevant.

Note 3: how to we rate and compare (benchmark) the resulting output structured data, what will be the coverage of the comparison part of this tool?

- wanted to find an example of llm comparison tool: found [this one](https://www.simonpcouch.com/blog/2025-04-01-gemini-2-5-pro) (here applied to Gemini 2.5 Pro) from Simon P. Couch ([via](https://simonwillison.net/2026/Jan/20/electricity-use-of-ai-coding-agents/) then [via](https://www.simonpcouch.com/blog/2026-01-20-cc-impact/)) : which lead me to a even more popular approach ? [https://inspect.aisi.org.uk/] .....  take-aways are:
  - use a repeat parameter (epoch) to "Evaluate each sample multiple times to better quantify variation"

**On where it sits in the ecosystem of LLM tools:** It is a LLM gateway: meaning it can call different LLM providers (local inference framework or cloud-hosted) with a rudimentary plugin system. If the project matures enough it could be beneficial the transition to a more established LLM gateway tool (like liteLLm, anyLLM).


## Getting started

1. [Ollama](https://ollama.com/download) should be installed and running
2. Clone the repository and install it with pip: `pip install .` (At this stage the package is not distributed, ie not published to PyPI, hence cannot be installed directly from PyPI)
    1. Or use `pip install -e .` if you want to install in editable mode.

## Usage

To run the example in `data/example1-ev`, use the command: `llm-extract --configfile=data/example1-ev/config.yaml`
