# adm-defender

**ADM Defense Agent** — an autonomous agent that handles airline Agency Debit Memos (ADMs) by deciding whether to dispute, pay, or escalate each case — with a hard code-enforced boundary for when it must defer to a human.

[▶ Watch the demo](https://drive.google.com/file/d/1o51QL0Luybmteu13k9QC4S9N8YnOKv2e/view?usp=drive_link)

Built for the Tabhi / Mondee internal operations use case: ~65,000 travel agents, ~$269 average ADM, 14-day dispute window. At that scale, ADMs are a direct P&L leak, not a UX nicety.

## Problem

Airlines issue ADMs to travel agencies when they detect ticketing errors — wrong fare calculation, rule violations, under-collected taxes, bad refunds. Every ADM either drains margin (if paid) or eats human hours (if disputed manually). This agent automates the dispute-or-pay decision.

## What it does

Given an incoming ADM notice, the agent:

1. Parses the ADM (ticket number, reason code, amount, deadline)
2. Pulls the PNR / booking record
3. Retrieves the relevant fare rule via RAG over real airline fare rule docs
4. Runs three deterministic verification tools (advance-purchase check, booking-class check, tax recalculation)
5. Reasons about whether the booking violates the cited rule
6. Decides one of: `DISPUTE` / `PAY` / `ESCALATE_TO_HUMAN`
7. Generates the appropriate output artifact

A hard decision boundary (amount > $500, confidence < 0.70, no strong rule match → ESCALATE) is enforced in code, not left to the LLM.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    ADM Defense Agent                     │
│                                                          │
│   [ADM notice]                                           │
│        │                                                 │
│        ▼                                                 │
│   ┌─────────────────────────────────────────────────┐    │
│   │           LangGraph State Machine               │    │
│   │   parse_adm → lookup_booking → retrieve_rule    │    │
│   │        → verify_calculation → analyze           │    │
│   │            │                                    │    │
│   │            ├─→ DISPUTE  → draft_letter          │    │
│   │            ├─→ PAY      → draft_pay_auth        │    │
│   │            └─→ ESCALATE → open_case             │    │
│   └─────────────────────────────────────────────────┘    │
│        │                                                 │
│        ▼                                                 │
│   [Output artifact + streamed reasoning trace]           │
└──────────────────────────────────────────────────────────┘
```

## Tech stack

| Layer | Choice |
|---|---|
| LLM | OpenRouter (`nvidia/nemotron-3-ultra-550b-a55b:free`) via OpenAI SDK |
| Agent framework | LangGraph (`StateGraph`) |
| Backend | FastAPI + WebSocket |
| RAG | Chroma + BGE-small embeddings via fastembed |
| Database | SQLite |
| Frontend | React 19 + Tailwind 4 + Vite |
| Fare rule corpus | 5 hand-authored Markdown docs (AA, EY, NH, AI, EK) |

## Repo structure

```
├── backend/
│   ├── app/              # FastAPI app + LangGraph agent
│   ├── data/             # Fare rule corpus, seed data
│   ├── tests/            # Pytest suite
│   └── requirements.txt
├── frontend/
│   ├── src/              # React + Tailwind UI
│   └── package.json
├── PRD.md                # Full product spec
└── arch.md               # Architecture deep-dive
```

## Seed data

10 mock ADMs across 5 airlines — 5 disputable, 3 legitimate (should PAY), 2 ambiguous (should ESCALATE). This distribution proves the agent has real judgment, not a reflex to dispute everything.

## Decision boundary

```
if amount_claimed > $500:              → ESCALATE
if agent_confidence < 0.70:            → ESCALATE
if no strong rule match:               → ESCALATE
else:                                  → DISPUTE or PAY
```

These checks are applied *after* the LLM call, in plain Python — the model cannot talk its way past them.

## What's real vs. simulated

- **Simulated**: fare rule corpus is hand-authored (not scraped PDFs); BSPLink submission is not integrated; tax table is hardcoded.
- **Real**: LangGraph state machine, RAG pipeline (real embeddings, real vector search, real metadata filtering), LLM calls against a real hosted model via OpenRouter, decision boundary logic, SQLite audit trail.

## API

```
GET  /health                       liveness
GET  /adm                          list all ADMs
GET  /adm/{adm_id}                 ADM + joined PNR
POST /agent/run/{adm_id}           full synchronous run
GET  /decision/{decision_id}       fetch a past decision
WS   /ws/agent/{adm_id}            stream agent steps live
```

## Alternative considered

OpenAI Assistants/Responses API tool-calling loop instead of LangGraph. LangGraph was chosen for the explicit state machine visualization; the native OpenAI tool-calling loop is a viable alternative noted here to signal awareness of the landscape.

## License

MIT
