# adm-defender — Backend

FastAPI + LangGraph backend for the ADM Defense Agent. Handles ADM parsing, PNR lookup, fare-rule RAG retrieval, deterministic verification, LLM-based analysis, and decision logging.

## Tech

| Component | Choice |
|---|---|
| Framework | FastAPI + native WebSocket support |
| Agent orchestration | LangGraph (`StateGraph`) |
| LLM | OpenRouter (`nvidia/nemotron-3-ultra-550b-a55b:free`) via `openai` SDK |
| RAG / vector store | Chroma (PersistentClient) + BGE-small embeddings via fastembed |
| Database | SQLite (3 tables: `pnr`, `adm`, `decision_log`) |

## Project structure

```
backend/
├── app/
│   ├── agent/           # LangGraph graph definition, nodes, tools
│   ├── api/             # FastAPI routes (REST + WebSocket)
│   ├── db/              # SQLite schema, seed data, connection
│   ├── rag/             # Chroma client, embedding function, retriever
│   └── main.py          # FastAPI app entry point
├── data/
│   ├── fare_rules/      # 5 hand-authored Markdown fare rule docs (AA, EY, NH, AI, EK)
│   └── seed/            # Seed SQL + expected_labels.json
├── tests/               # Pytest suite
├── requirements.txt
├── .env                 # API keys (not committed)
└── .env.example         # Env template
```

## LangGraph agent pipeline

```
parse_adm → lookup_booking → retrieve_rule → verify_calculation → analyze
    │                                                              │
    ├── DISPUTE  → draft_letter     ←──────────────────────────────┤
    ├── PAY      → draft_pay_auth   ←──────────────────────────────┤
    └── ESCALATE → open_case        ←──────────────────────────────┘
                       │
                       ▼
              submit_decision → return
```

The graph always runs the full pipeline — even cases that will be escalated — so the evidence trail is complete for human reviewers.

## Decision boundary (enforced in code, not in the prompt)

```python
if amount_claimed > $500:              → ESCALATE   # hard threshold
if agent_confidence < 0.70:            → ESCALATE   # model uncertainty
if no strong rule match:               → ESCALATE   # never fabricate
else:                                  → DISPUTE or PAY
```

## Deterministic verification tools

| Tool | What it checks |
|---|---|
| `check_advance_purchase` | Fare basis advance-purchase days vs. booking-to-departure gap |
| `check_booking_class_match` | Fare basis leading letter vs. ticketed booking class |
| `verify_tax_calculation` | Recompute expected tax vs. PNR's recorded tax |

These give the LLM verified facts to reason over for exact arithmetic and date math.

## RAG design

- Chunks: one per fare-basis rule block (split on `##` headings)
- Self-contained: each chunk gets the document's preamble prepended so retrieval is single-hop
- Embedding: BGE-small-en-v1.5 with asymmetric query prefix
- Filtering: `airline_code` metadata filter applied *before* semantic search — an Emirates rule can never be cited against an Air India ADM

## API

```
GET  /health                       liveness
GET  /adm                          list all ADMs
GET  /adm/{adm_id}                 ADM + joined PNR
POST /agent/run/{adm_id}           full synchronous run → DecisionOut
GET  /decision/{decision_id}       fetch a past decision
WS   /ws/agent/{adm_id}            stream node-by-node updates
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env     # add your OpenRouter API key
uvicorn app.main:app --reload
```

## Testing

```bash
pytest
```

## Seed data

10 ADMs (5 DISPUTE / 3 PAY / 2 ESCALATE) across 5 airlines. Expected labels in `data/seed/expected_labels.json` are used only by the eval script — the agent never sees them.
