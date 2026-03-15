# CyclopsRD
### Detecting Political Bias in Highway Maintenance Decisions
> **Hackathon Project Proposal**

---

> *"Making Highway Decisions Transparent."*

---

## Executive Summary

CyclopsRD is a transparency tool that compares engineering-based highway maintenance priorities with actual allocation patterns, revealing potential political or administrative bias in infrastructure decision-making.

**The Core Insight:** Highway maintenance decisions should follow objective engineering criteria. But do they? CyclopsRD computes a **Transparency Gap** — the difference between where infrastructure resources *should* go (engineering priority) vs. where they *actually* go (observed allocation). Large gaps signal potential misallocation worth investigating.

This hackathon prototype demonstrates the concept using open data from **Jambi, Indonesia** — a city with reasonable OSM coverage, defined administrative districts (kecamatan), and documented concerns about infrastructure equity across its urban-rural corridor.

---

## Problem Statement

Highway maintenance prioritization in most countries lacks transparency. The public, civil engineers, and even mid-level administrators rarely have access to the data or tools needed to evaluate whether infrastructure resources are allocated based on engineering necessity or shaped by political influence.

| The Current Reality | What This Creates |
|---|---|
| Maintenance records are fragmented or unpublished | Underserved roads deteriorate faster, raising safety risks |
| No standard methodology to compare need vs. allocation | Freight costs rise in structurally neglected corridors |
| Citizens suspect political favoritism but cannot prove it | Trust in public institutions erodes |
| Accountability mechanisms are reactive, not analytical | No feedback loop between data and spending decisions |

**Why Now?** Open geospatial data (OpenStreetMap, BPS Indonesia), graph analysis libraries (NetworkX, OSMnx), and web mapping tools (Leaflet, Deck.gl) now make this analysis feasible within a hackathon timeframe. The barrier is no longer technical — it is organizational will.

---

## Improved Core Concept

The concept has been sharpened in three key ways.

### 1. Anchor to a Real City: Jambi

Rather than a generic prototype, the demo uses Jambi's road network. This provides:

- Real OSM road data with highway classifications (trunk, primary, secondary, tertiary)
- Official kecamatan boundary polygons from BPS Indonesia
- A plausible observed allocation proxy: road condition reports from Qlue / Lapor.go.id citizen platforms
- A compelling story — Jambi's infrastructure inequality between urban core and peri-urban kecamatan is well-documented and underreported

### 2. Strengthen the Engineering Score

The scoring model uses five validated metrics:

| Factor | Weight | Source | Rationale |
|---|---|---|---|
| Road Hierarchy | 30% | OSM highway tag | Trunk > primary > secondary > tertiary |
| Betweenness Centrality | 25% | NetworkX on OSM graph | How often a road lies on shortest paths |
| Connectivity Degree | 20% | OSM intersection count | Roads connecting more routes have higher need |
| Traffic Volume Proxy | 15% | OSM lanes + link roads | More lanes = higher usage expectation |
| Population Exposure | 10% | BPS census grids | Roads serving denser areas have higher stakes |

```
Priority Score = 0.30 × Road Hierarchy
              + 0.25 × Betweenness Centrality
              + 0.20 × Connectivity Degree
              + 0.15 × Traffic Volume Proxy
              + 0.10 × Population Exposure
```

> **Why not use actual traffic data?** Real traffic counts are rarely available in open datasets. The proxy (lanes + link road type) is a validated workaround used in academic road prioritization literature. It's transparent, reproducible, and improvable when better data exists.

### 3. The Transparency Gap — Refined

The gap is computed at two levels.

**Segment Level (individual road):**

| Road | Eng. Rank | Alloc. Rank | Gap | Signal |
|---|---|---|---|---|
| Jl. Sultan Thaha | #2 | #14 | -12 | 🔴 Under-prioritized |
| Jl. Gatot Subroto Jambi | #18 | #4 | +14 | 🟢 Over-prioritized |
| Jl. Hayam Wuruk | #7 | #8 | -1 | ⚪ Within range |

**District Level (aggregate):**

| District | Eng. Need % | Alloc. % | Gap | Signal |
|---|---|---|---|---|
| Kota Baru | 22% | 37% | +15% | 🔴 Over-resourced |
| Paal Merah | 30% | 18% | -12% | 🔵 Under-resourced |
| Jelutung | 18% | 20% | +2% | ⚪ Within range |
| Danau Sipin | 25% | 13% | -12% | 🔵 Under-resourced |

---

## Key Improvements Over Original Concept

### Improvement 1: The Anomaly Threshold

Not every gap is meaningful. The improved system uses statistical thresholds: gaps within **1 standard deviation** of the mean are marked as "within range". Only outliers beyond that threshold trigger a flag. This prevents false alarms and makes the tool credible to practitioners.

### Improvement 2: Temporal Dimension

A single snapshot is interesting. A trend is compelling. The improved prototype tracks the Transparency Gap over multiple simulated time periods (quarterly). This answers the more important question: is a district's under-allocation getting *worse or improving* over time?

### Improvement 3: Narrative Explanation Engine

Instead of just showing a number, each flagged road or district gets an auto-generated plain-language explanation:

> **Example Auto-Explanation**
>
> *Jl. Sultan Thaha scores #2 in engineering priority because it connects 5 major arterials, has the highest betweenness centrality in central Jambi, and serves an estimated 90,000 vehicles/day. Despite this, it ranks #14 in observed maintenance allocation. This 12-rank gap places it in the top 10% of under-prioritized roads in the dataset. No administrative reason for this gap is currently documented.*

### Improvement 4: Confidence Indicators

The tool is honest about data quality. Each score displays a confidence level (**High / Medium / Low**) based on OSM data completeness for that segment. Roads with sparse tagging are flagged so users know to treat their scores with caution.

### Improvement 5: District Comparison Mode

Rather than just showing absolute gaps, the tool ranks all kecamatan by gap magnitude, creating a leaderboard. Districts with consistently large gaps across multiple periods rise to the top as **systemic anomalies** rather than one-time noise.

---

## Technical Architecture

### Data Pipeline

1. Fetch Jambi road network via **OSMnx** (Python) — filters for highway tags above footpath level
2. Download kecamatan boundary GeoJSON from **BPS Indonesia** open data portal
3. Pull citizen-reported road issues from **Qlue / Lapor API** (or use cached sample for hackathon)
4. Compute graph metrics using **NetworkX**: betweenness centrality, degree centrality, connected components
5. Spatial join road segments to districts using **GeoPandas**
6. Score, rank, and calculate gaps; export to GeoJSON + JSON

### Frontend

- **Leaflet.js** map with road segments colored by Engineering Priority Score (red → yellow → green)
- District polygon overlay with choropleth coloring by Transparency Gap
- Click on any segment: panel shows rank, score breakdown, gap, and plain-language explanation
- District dashboard: bar chart comparing Engineering Need % vs Allocation % per kecamatan
- Time slider (if temporal data included): watch gap evolution across quarters

### Tech Stack

| Component | Tool | Why |
|---|---|---|
| Road graph | OSMnx + NetworkX | OSM-native, centrality built-in |
| Spatial ops | GeoPandas + Shapely | District joins, polygon ops |
| Backend API | FastAPI (Python) | Lightweight, fast to build |
| Map frontend | Leaflet.js | Open, hackathon-friendly |
| Charts | Chart.js | Simple bar/line charts |
| Data format | GeoJSON + JSON | Map-ready, no DB needed |

---

## Demo Walkthrough (5 Minutes)

| Step | Action | What Judges See |
|---|---|---|
| 1 | Open the map | Jambi road network loads. Roads color-coded red (high engineering priority) to green (low). Spatial structure is immediately visible. |
| 2 | Toggle district overlay | Kecamatan boundaries appear. Districts shaded by Transparency Gap — dark red = over-allocated, dark blue = under-allocated. |
| 3 | Click Jl. Sultan Thaha | Side panel opens: rank #2 engineering, rank #14 allocation, gap -12. Score breakdown shown. Auto-explanation generated. |
| 4 | Open district dashboard | Bar chart: Kota Baru gets 37% of allocation but only 22% engineering need. Paal Merah the inverse. |
| 5 | Advance the time slider | The gap in two kecamatan widens over simulated quarters — showing the pattern is not a data artifact but a persistent trend. |

---

## Risks & Honest Limitations

| Risk | Severity | Mitigation |
|---|---|---|
| Observed allocation data is simulated | High | Be explicit in the demo: "simulated from citizen reports." Frame it as a methodology demonstration, not a real audit. |
| Engineering weights are arbitrary | Medium | Document the weights clearly. Offer a weight-tuning slider in the UI so judges see the model is transparent and adjustable. |
| OSM data quality varies by district | Medium | Show confidence indicators on each segment. Low-confidence roads are flagged, not hidden. |
| Tool could be misused for political attack | Medium | The UI's language is consistently analytical: "warrants investigation," never "proves corruption." |
| Scope too large for 1–2 days | High | Scope to 3–4 kecamatan in central Jambi only. Full city coverage is a stretch goal. |

---

## Hackathon Execution Plan

### If Solo
Focus entirely on the data pipeline and one clean visualization. A compelling static map with real data beats a broken interactive prototype.

### If Team of 2

| Person 1: Data + Backend | Person 2: Frontend |
|---|---|
| OSMnx road network extraction | Leaflet map setup |
| NetworkX centrality computation | Road segment color coding |
| District spatial join (GeoPandas) | Click-to-panel interaction |
| Scoring + gap calculation | District bar chart (Chart.js) |
| FastAPI endpoint serving GeoJSON | Responsive layout |

### If Team of 3+

- Add person for temporal simulation + time slider
- Add person for auto-explanation generation (template + data merge)
- Add person for polish: animations, confidence badges, methodology panel

### Recommended Timeline (24-hour hackathon)

| Hours | Milestone |
|---|---|
| 0–3h | Data pipeline working: OSM graph loaded, centrality computed, saved to GeoJSON |
| 3–6h | Scoring formula implemented; district join complete; gap calculated for all segments |
| 6–10h | Leaflet map showing road segments colored by engineering score |
| 10–14h | District overlay + side panel on click working |
| 14–18h | District dashboard chart + auto-explanation text |
| 18–22h | Bug fixing, data quality review, UI polish |
| 22–24h | Demo rehearsal, slide prep, README |

---

## Future Roadmap

### Version 2: Real Data Integration
- Direct API integration with municipal maintenance budget records
- Partnership with Lapor.go.id for real-time citizen issue density
- Historical data going back 5 years to establish baselines

### Version 3: Expanded Coverage
- Multi-city deployment (Palembang, Pekanbaru, Bengkulu)
- Configurable weight model validated by transport engineers
- Automated anomaly scoring with statistical significance testing

### Version 4: Policy Integration
- Export reports in formats used by BAPPENAS (national planning agency)
- Budget recommendation module: where should next year's allocation go?
- Citizen dashboard: submit road conditions directly, feed into scoring

> **The Long-Term Vision:** CyclopsRD could become the standard methodology for infrastructure equity auditing — not just in Indonesia, but in any country with OpenStreetMap coverage. The open-source model means any civil society organization, journalist, or government accountability office can run it.

---

## Pitch Notes for Judges

**01 — The methodology is neutral**
We are not accusing anyone. We are building the infrastructure for accountability. The tool reveals patterns; humans investigate causes.

**02 — The data is real**
The road network, centrality scores, and district boundaries are computed from real OpenStreetMap data for Jambi, not made up.

**03 — It scales**
Any city with OSM data can run this. The methodology is portable, open-source, and designed for replication.

---

*CyclopsRD — "Auditing Infrastructure with Data."*

---

# Startup Strategy: Moving from Hackathon to CyclopsRD

Great — now we move from **hackathon idea → real startup strategy**.

The key question investors ask is:

> *“Why will this become a large company instead of just a small analytics tool?”*

To answer that, we need **one killer feature** and **one strong moat**.

---

## 1. The Killer Feature: Infrastructure Decision Audit Engine

This is what makes your startup unique. Most infrastructure tools show road conditions, traffic, or asset inventory. But **no platform audits infrastructure decisions themselves**.

### “Decision Audit”

Your system automatically evaluates whether **infrastructure decisions align with engineering logic**.

Example output:
```
Highway Segment: A12
Engineering Priority Rank: #3
Maintenance Allocation Rank: #17

Decision Alignment Score: 32 / 100
Flag: Potential underinvestment
```

The system does **not accuse anyone**. It simply highlights **misalignments**. This turns your platform into an **auditing tool for infrastructure decisions.**

---

## 2. Why This Is Rare

Current transport tools (like StreetLight Data or INRIX) focus on traffic monitoring and asset management. None focus on **decision transparency**. That’s your niche.

---

## 3. The Real Moat: The Infrastructure Decision Model

The moat is the data accumulated over time. Your platform learns:
* How infrastructure priorities are usually calculated.
* How governments allocate budgets.
* What “normal” infrastructure allocation patterns look like.

Eventually, you build the **largest dataset of infrastructure decision patterns**, allowing you to benchmark infrastructure governance globally.

---

## 4. The Product Evolution Roadmap

1.  **Stage 1 — Hackathon / MVP:** Basic platform using OpenStreetMap to prove the concept of transparency gaps.
2.  **Stage 2 — Professional Tool:** Add real datasets (budgets, surveys) for infrastructure consultants and planning agencies ($10k–$50k/year per org).
3.  **Stage 3 — Infrastructure Governance Platform:** A full GovTech platform with Budget Transparency, Project Allocation Analysis, and Policy Simulation.

---

## 5. The Long-Term Vision: “Bloomberg for Infrastructure Governance”

A platform where governments, banks (World Bank, ADB), researchers, and NGOs analyze infrastructure investment and project prioritization.

---

## 6. The Startup Story

> “Infrastructure decisions shape economies, yet they remain opaque. We are building the first platform that audits infrastructure decisions using data. **We bring transparency to infrastructure spending.**”

---

## 7. A Very Strong Startup Name: **CyclopsRD**

*"Seeing infrastructure decisions clearly."*

---

## 8. Brutally Honest Insight

Your biggest challenge will not be technology—it will be **politics**. That’s why the **consultant market** is your best first entry point.

---

## 9. The 7-Slide Investor Pitch Deck

Here is the structure to win over investors:

1.  **Title:** **CyclopsRD** — *Seeing infrastructure decisions clearly.*
2.  **The Problem:** Infrastructure spending is a black box. Trillions are spent, but who audits the *choices*? Bias leads to inefficiency and safety risks.
3.  **The Solution:** The **Infrastructure Decision Audit Engine**. A data-driven way to compare engineering needs vs. actual budget allocation.
4.  **The Tech/Magic:** Our proprietary **Decision Alignment Score** that flags systemic anomalies in governance.
5.  **The Moat:** The **Infrastructure Decision Model**. The first global dataset of governance patterns.
6.  **Market/Roadmap:** From Hackathon MVP to $xxxB GovTech market. Targeting WB/ADB and elite consultants first.
7.  **The Vision:** Becoming the "Bloomberg for Infrastructure." Transforming how nations build.

