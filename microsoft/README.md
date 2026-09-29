# 🧠 VentureScope — Venture Intelligence Platform

> **See the Market. Map the Opportunity. Simulate the Venture.**

An evidence-grounded venture intelligence platform that reconstructs the market around a business venture, maps where opportunity exists geographically, models behavioral adoption across a 500-participant synthetic micro-population, evaluates stochastic outcomes across 10,000 Monte Carlo runs, and continuously learns from previous analyses using **Hindsight by Vectorize**.

---

## 🎯 What is VentureScope?

VentureScope is structured strictly around **Two Core Features**:

1. **Market Overview**:
   - 11 calibrated Hyderabad micro-markets mapped with empirical retail evidence
   - 4-step evidence chains per locality (`Observed → Calculated → Inferred → Modeled`)
   - 0–24 month market trajectory projections across Optimistic, Expected, and Pessimistic scenarios
   - **Hindsight Longitudinal Memory**: Retains market states and detects structural changes over time ("What Changed?") with citations and reflect summaries

2. **Venture Deployment Simulation**:
   - **Venture X-Ray**: Automated web inspection of venture storefronts (pricing, positioning, differentiators)
   - **500-Person Calibrated Synthetic Market**: Micro-population calibrated against Hyderabad demographic profiles, spending bands, and category affinities
   - **7-Stage Customer Journey Funnel**: Awareness → Interest → Consideration → Intent → Purchase → Repeat with explicit drop-off trace
   - **Derived CAC & Acquisition Modeling**: Channel breakdown across Meta, Google Search, Influencers, and Organic
   - **Monte Carlo Stochastic Engine**: ~10,000 parameterized business trial runs yielding P10, P25, P50, P75, P90 percentile outcome bands and break-even probability distributions
   - **Systematic Stress Testing**: Macroeconomic, competitive, and supply-chain shock modeling (CAC inflation, price wars, churn decay, COGS inflation)
   - **2D Decision Surface**: Parameter grid across (Product Price vs Marketing Budget) identifying viable envelopes and burn traps
   - **Investor Exposure Balance Sheet**: Objective transparency across Strengths, Risks, and Critical Unknowns without arbitrary "Invest / Don't Invest" binary scores

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      FRONTEND                           │
│     React + TypeScript + Vite + Tailwind CSS v4         │
│  ┌─────────────────────────┐   ┌─────────────────────┐  │
│  │     Market Overview     │   │ Venture Simulation  │  │
│  │ (11 Corridors, Chains,  │   │  (500-Cohort, MC,   │  │
│  │    Hindsight Memory)    │   │  Stress, Decision)  │  │
│  └────────────┬────────────┘   └──────────┬──────────┘  │
│               │                           │             │
│               └─────────────┬─────────────┘             │
│                             │                           │
│                       REST API Calls                    │
└─────────────────────────────┼───────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────┐
│                          BACKEND                        │
│                Python 3.10+ & FastAPI                   │
│  ┌──────────────────────────┼────────────────────────┐  │
│  │                   API ROUTERS                     │  │
│  │  /api/markets  /api/simulation  /api/hindsight    │  │
│  └──────────┬───────────────┬──────────────┬─────────┘  │
│             │               │              │            │
│  ┌──────────┴──────┐ ┌──────┴──────┐ ┌─────┴─────────┐  │
│  │ Market Data &   │ │ Simulation  │ │   Hindsight   │  │
│  │ Evidence Store  │ │   Engines   │ │ Memory Layer  │  │
│  │  (11 Hyderabad  │ │• 500-Cohort │ │ • Retain      │  │
│  │   Corridors)    │ │• Monte Carlo│ │ • Recall      │  │
│  │                 │ │• Stress Test│ │ • Reflect     │  │
│  │                 │ │• 2D Surface │ │ • Changes     │  │
│  └─────────────────┘ └─────────────┘ └───────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🧠 Hindsight by Vectorize Integration

Hindsight is the foundational longitudinal memory layer beneath both core features. It is **not** a simple database or local storage wrapper; it is an active cognitive memory system.

### Core Hindsight Operations

| Operation | Implementation in VentureScope | Trigger |
|-----------|--------------------------------|---------|
| **Retain** | Stores market state snapshots (`type:market_state`), competitor entries, customer segment discoveries, and venture simulation runs | After analysis and simulation deployment |
| **Recall** | Semantic retrieval of prior observations via TEMPR multi-strategy search | When comparing current state to baseline |
| **Reflect** | Synthesizes answers with confidence scores and citations about what changed | Displayed in "What Changed?" panel |
| **Change Detection** | Dual semantic + deterministic comparison of prices, competitor counts, and emerging hotspots | Automatic comparison flow |

---

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.10+
- Node.js 18+ & npm

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment (optional)
python -m venv venv
venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables (.env)
cp .env.example .env
```

Set the following variables in your `.env`:
```env
HINDSIGHT_API_TOKEN=hsk_your_token_here
HINDSIGHT_MODE=cloud   # (or "mock" for offline testing)
HINDSIGHT_BANK_ID=venturescope-market-intelligence
```

Run tests:
```bash
python -m pytest app/tests/ -v
```

Start backend API:
```bash
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Build verification
npm run build

# Start dev server
npm run dev
```

Navigate to `http://localhost:5173`.

---

## 🔐 Data Integrity & Evidence Classification

Every data point in VentureScope is classified according to strict evidentiary standards:

| Classification | Definition | Badge Color |
|---------------|------------|-------------|
| **Observed** | Directly verified from public filings, retail directories, or storefronts | 🟢 Emerald |
| **Calculated** | Mathematical ratio derived from observed inputs (e.g. density per km²) | 🔵 Blue |
| **Inferred** | Logical inference based on demographic overlays and consumer behavior | 🟡 Amber |
| **Modeled** | Algorithmic synthesis or stochastic simulation (e.g. Monte Carlo) | 🟣 Violet |

VentureScope avoids misleading certainty: projections are labeled with percentile bands (P10–P90), scenario assumptions, and explicit stress test impacts.

---

## 🏆 Hackathon Alignment

- **Innovation (30%)**: Interactive market intelligence & venture deployment simulation with real 500-participant synthetic population.
- **Hindsight Memory (25%)**: Longitudinal memory foundation powering the "What Changed?" analysis over time.
- **Technical Excellence (20%)**: Deterministic financial math, ~10,000-run Monte Carlo engine, and clean TypeScript/React architecture.
- **UX & Design (15%)**: Linear-inspired editorial light theme, high-density metric cards, and responsive charts.
- **Real-World Impact (10%)**: De-risks early-stage capital allocation for founders and investors before committing capital.
