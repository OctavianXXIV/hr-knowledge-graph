# HR Knowledge Graph with Graph-Grounded RAG

Portfolio project for an Associate Data Scientist role at SAP. The goal is to
build it AND be able to explain every line and decision in an interview.

## Stack
- Python 3.11, venv in .venv, pandas, matplotlib
- Neo4j AuraDB (credentials in .env; never print, log or commit them), rdflib, pyshacl
- Later: sentence-transformers, Chroma, Ollama, Streamlit

## Layout
data/raw (IBM CSV, not committed), data/synthetic, data/external, data/rdf,
src/, notebooks/, policies/, ontology/, shapes/, queries/, eval/, docs/, logs/

## How to work with me (learning mode)
- For any new task, propose a short plan first and wait for my OK.
- Build in small steps: one notebook section or one function at a time.
- After each step, explain in 3–5 lines what the code does and why you chose
  this approach over the obvious alternative.
- Leave judgement calls to me. Mark them `# TODO(me):` and ask me the question
  instead of answering it.
- When I write code, review it like a senior data scientist: correctness first,
  then clarity. Point out problems; don't silently rewrite my code.
- I run notebook cells myself and paste the output back to you.
- Keep code plain (pandas + matplotlib). Ask before adding a library.
- Log design decisions I make in NOTES.md: date, decision, reason, alternative rejected.