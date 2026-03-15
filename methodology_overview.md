# CyclopsRD — Technical Methodology

> *This document explains the complete scoring, allocation, and audit methodology used by CyclopsRD. It is the technical companion to the [README](README.md).*

---

## Overview

CyclopsRD's methodology is built on one principle: **if infrastructure allocation were perfectly fair, the roads receiving funding would be the same roads that engineering analysis says need it most.** Any deviation from this ideal reveals a "Transparency Gap" worth investigating.

The pipeline proceeds in three stages:

```
     STAGE 1                  STAGE 2                  STAGE 3
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│ ENGINEERING  │         │  POLITICAL   │         │  DECISION    │
│ PRIORITY     │────────▶│  ALLOCATION  │────────▶│  AUDIT       │
│              │         │              │         │              │
│ "What SHOULD │         │ "What DID    │         │ "Did the     │
│  be funded?" │         │  get funded?"│         │  decision    │
│              │         │              │         │  make sense?"│
└─────────────┘         └──────────────┘         └──────────────┘
   Pure math              Real politics            The verdict
```

---

## Stage 1: Engineering Priority Score
> **Implementation:** [`pipeline/03_score_and_rank.py`](pipeline/03_score_and_rank.py)

### What It Measures
The Engineering Priority Score quantifies the **objective infrastructure importance** of every road segment in the network. A road with a high score is one that — from a pure engineering standpoint — should receive maintenance priority.

### The Formula

```
Priority Score = 0.25 × Hierarchy
               + 0.20 × Betweenness Centrality
               + 0.20 × Normalized Length
               + 0.15 × Connectivity Degree
               + 0.10 × Lane Count (Traffic Proxy)
               + 0.10 × Population Exposure
```

### Factor Breakdown

| Factor | Weight | Data Source | What It Captures |
|---|---|---|---|
| **Road Hierarchy** | 25% | OSM `highway` tag | Official classification. Trunk and Primary roads are the economic skeleton. A collapsed arterial disrupts the entire city. |
| **Betweenness Centrality** | 20% | NetworkX edge centrality | How many shortest paths in the graph pass through this segment. High betweenness = critical bottleneck. |
| **Normalized Length** | 20% | OSM geometry | Longer road segments represent larger capital investments. A 2km segment failing has 4× the impact of a 500m segment. |
| **Connectivity Degree** | 15% | OSM node degree | Number of intersections this road connects. Hub roads are more critical than dead-end streets. |
| **Traffic Proxy (Lanes)** | 10% | OSM `lanes` tag | Number of lanes as a proxy for traffic volume. More lanes = higher usage expectation. Default: 2 if missing. |
| **Population Exposure** | 10% | Placeholder (0.5) | Proxy for population density near the road. Future: integrate BPS census grid data. |

> **Why these weights?** They are informed by established road prioritization frameworks (World Bank, HDM-4) adapted for data availability in Indonesian cities. Hierarchy and Centrality receive the highest weights because they capture both administrative importance and network-critical function. Length is weighted equally to centrality because longer continuous segments represent proportionally larger maintenance investments.

### Ensuring Unique Ranks

In a real municipal budget, two roads cannot share the same rank — one must be funded first. To guarantee strictly unique rankings:

1. A **deterministic micro-jitter** (uniform random noise, seed=42, magnitude <10⁻⁶) is added to each score
2. Pandas `rank(method='first')` is applied to resolve any remaining ties by order of appearance

Result: Every road segment receives a unique rank from **1** (most critical) to **N** (least critical), where N = total segments in the network (currently 1,038 segments in Kota Jambi, spanning 412.6 km).

---

## Stage 2: Political Allocation Simulation

### The Core Insight

> If allocation perfectly followed engineering priority, the top 25% of roads by Engineering Rank would be the same as the 25% receiving funding. But **politics doesn't work that way.**

CyclopsRD models this reality by injecting a **Political Bias Factor** derived from real-world legislative representation data.

### Data Source: 2024 DPRD Kota Jambi Elections

We use the actual seat distribution from the 2024 Regional People's Representative Council (DPRD) elections for Kota Jambi. The 45 total seats are divided across 5 Electoral Districts (Dapil):

| Dapil | Kecamatan(s) | Seats | vs. Average (9) | Bias Effect |
|---|---|---|---|---|
| **Dapil 1** | Kota Baru | 6 | -3 below avg | **-10%** allocation penalty |
| **Dapil 2** | Alam Barajo | 8 | -1 below avg | **-3%** slight penalty |
| **Dapil 3** | Telanaipura, Danau Sipin, Danau Teluk | 8 | -1 below avg | **-3%** slight penalty |
| **Dapil 4** | Pelayangan, Jambi Timur, Pasar Jambi, Jelutung | 11 | +2 above avg | **+7%** bias boost |
| **Dapil 5** | Jambi Selatan, Paal Merah | 12 | +3 above avg | **+10%** strongest bias |

### The Hypothesis

Districts with **more legislative seats** have greater political influence over municipal budget allocation. Their roads are more likely to receive maintenance funding — even if they don't rank highest in engineering priority.

### The Allocation Propensity Formula
> **Implementation:** [`pipeline/04_simulate_allocation.py`](pipeline/04_simulate_allocation.py)

```
Allocation Propensity = (Inverted Engineering Rank ^ 0.8) × (1.0 + Political Bias) + Jitter

Where:
  Inverted Rank = (MaxRank - Rank) / MaxRank     ← Higher priority = higher propensity
  Political Bias = ((DapilSeats - 9) / 9) × 0.3  ← Scaled from DPRD seat distribution
  Jitter = Uniform(-0.1, +0.1)                  ← Simulates real-world noise/irregularities
```

### Budget Constraint

Municipal budgets are finite. We model this by allocating funding to only the **top 25%** of road segments ranked by Propensity Score:

```python
budget_count = int(len(all_roads) * 0.25)  # ≈ 260 of 1,038 segments
funded = roads.sort_values('propensity', ascending=False).head(budget_count)
```

**Result:**
- Roads with `is_allocated = 1` → Funded this fiscal year
- Roads with `is_allocated = 0` → Not funded

The political bias means that some **high-priority roads in under-represented districts get skipped**, while some **low-priority roads in well-represented districts get funded**. This is the "transparency gap" that CyclopsRD exposes.

---

## Stage 3: The Decision Audit
> **Implementation:** [`pipeline/05_calculate_gap.py`](pipeline/05_calculate_gap.py)

### What We're Measuring

The Decision Audit answers: **"For each road, was the allocation decision justified by engineering need — or warped by political influence?"**

### Alignment Logic

We compare two binary classifications:
- **Engineering Need:** Is the road in the Top 25% of Engineering Rank?
- **Allocation Status:** Did it receive funding?

| Engineering Top 25%? | Allocated? | Alignment Score | Flag | Interpretation |
|---|---|---|---|---|
| ✅ Yes | ✅ Yes | **100** | 🟢 Aligned | Correctly funded — the system works |
| ❌ No | ❌ No | **100** | 🟢 Aligned | Correctly deferred — limited budget, rational triage |
| ✅ Yes | ❌ No | **50** | 🟡 Moderate (Neglect) | Critical infrastructure ignored — investigate why |
| ❌ No (Bottom 50%) | ✅ Yes | **30** | 🔴 Significant (Favoritism) | Low-need road funded — possible political influence |
| Middle 25-50% | ✅ Yes | **80** | 🟢 Aligned | Borderline — acceptable within normal variance |

### District-Level Aggregation

Individual road-level scores are aggregated to the Kecamatan level using **length-weighted** statistics:

```
Engineering Need % = Σ(priority_score × length) in district / Σ(priority_score × length) citywide × 100

Financial Allocation % = Σ(allocated_length) in district / Σ(allocated_length) citywide × 100

Transparency Gap % = Allocation % - Need %
```

**Why length-weighted?** A 3km arterial receiving funding is fundamentally different from a 200m residential street receiving funding. Length-weighting ensures the percentages reflect the **physical scale** of infrastructure investment, not just a count of segments.

---

## Honest Limitations

CyclopsRD is a **methodology demonstration**, not a live government audit. We are transparent about these boundaries:

| Limitation | What We Do About It |
|---|---|
| Real allocation data doesn't exist in machine-readable form | We simulate it transparently using political representation as a proxy |
| Engineering weights are calibrated, not "ground truth" | Weights are documented and adjustable; the methodology is auditable |
| Population data is a uniform placeholder (0.5) | Future: integrate BPS Indonesia census grids for real density |
| OSM data quality varies by district | Future: add confidence indicators per segment |
| The tool could be misused for political attacks | All language is analytical: "warrants investigation", never "proves corruption" |

> **The technology works. The data integration is a partnership problem, not an engineering one.**

---

## References

- **OpenStreetMap Contributors** — Road network data for Kota Jambi
- **Badan Pusat Statistik (BPS)** — Indonesian district administrative boundaries
- **KPU Kota Jambi** — 2024 DPRD election results and Dapil seat allocations
- **World Bank HDM-4** — Highway Development and Management framework for road prioritization
- **NetworkX Documentation** — Edge betweenness centrality algorithm

---

<p align="center">
  <strong>CyclopsRD</strong><br>
  <em>"We don't just map potholes. We map the decisions behind them."</em>
</p>
