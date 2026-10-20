# hr-knowledge-graph

A knowledge graph built from the IBM HR Analytics employee attrition dataset, stored in Neo4j and modelled with RDF and SHACL.

> **Status:** early setup. The project structure, Python environment and Neo4j connection check are in place. The ontology, data loading and queries are still to come.

## Tech stack

- **Python 3.12**: pandas and numpy for data prep, Jupyter for exploration
- **Neo4j** (for example a free Aura instance) as the graph database, via the official `neo4j` driver
- **rdflib** and **pySHACL** for the RDF ontology and SHACL validation
- **ruff** for linting

## Getting started

### 1. Clone and create a virtual environment

```bash
git clone <repo-url> hr-knowledge-graph
cd hr-knowledge-graph
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Download the dataset

Download the [IBM HR Analytics Employee Attrition & Performance](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset) dataset from Kaggle and put the CSV in `data/raw/`:

```
data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv
```

Files in `data/raw/` are git-ignored, so the dataset is never committed.

### 3. Configure Neo4j credentials

Copy the example file and fill in your instance details:

```bash
cp cred.env.example cred.env
```

```dotenv
NEO4J_URI=neo4j+s://<instance-id>.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=<password>
```

`cred.env` is git-ignored. Never commit real credentials.

### 4. Check the connection

```bash
python src/check_connection.py
```

If it works, you'll see `Connected to Neo4j`.

## Project structure

```
hr-knowledge-graph/
├── data/
│   ├── raw/          # Original Kaggle CSV (git-ignored)
│   ├── external/     # Other third-party reference data
│   ├── synthetic/    # Generated or augmented data
│   └── rdf/          # Graph data serialised as RDF
├── ontology/         # Ontology / schema definitions for the HR domain
├── shapes/           # SHACL shapes for validating the graph
├── policies/         # HR policy documents and rules modelled in the graph
├── queries/          # Cypher / SPARQL queries
├── notebooks/        # Jupyter notebooks (e.g. 01_eda.ipynb)
├── src/              # Python source code
│   └── check_connection.py
├── eval/             # Evaluation scripts and results
├── docs/             # Project documentation
├── logs/             # Run logs (*.log is git-ignored)
├── cred.env.example  # Template for Neo4j credentials
└── requirements.txt
```

Most folders are placeholders for now (they only contain a `.gitkeep`).

## Development

Lint and format with ruff:

```bash
ruff check .
ruff format .
```

To use the virtual environment in Jupyter, register it as a kernel:

```bash
python -m ipykernel install --user --name hr-knowledge-graph
```

## Data source and license

- Dataset: [IBM HR Analytics Employee Attrition & Performance](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset), a fictional dataset created by IBM data scientists. See Kaggle for its terms.
- Code: [MIT License](LICENSE) © 2026 Shivanshu Mall
